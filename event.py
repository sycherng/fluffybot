import asyncio, datetime, string
import async_db as db, secrets, reminder
import user

async def respond(bot, message):
    pass

async def prefix_respond(bot, message):
    await create_event(bot, message)
    await edit_event_field(bot, message)
    await event_rvsp(bot, message)
    await set_reminder(bot, message)
    await event_list(bot, message)

async def create_event(bot, message):
    '''|user|
    (Bot object, Message object) -> None

    Command: <prefix>create event

    Checks: message author rank
    Actions: creates an event object represented by a new entry in bot's "event" table.
    '''
    command_opener = 'create event'
    if message.content == command_opener and await db.user_has_permission(message.author.id, command_opener):
        print('creating event')
        result_list = await db.fetch('SELECT max(event_id::int) FROM event')
        max_event_id = result_list[0]['max'] #int
        if max_event_id < 99999:
            new_event_id = (str(max_event_id + 1)).zfill(5)
            try: await db.execute(f"INSERT INTO event (event_id, host_id) VALUES ('{new_event_id}', {message.author.id})")
            except Exception as error:
                await user.notify_owner(bot, command_opener, message.author, error)
            else:
                await bot.send_message(message.author, f"Event#{new_event_id} created." )
        else:
            await db.execute(f"UPDATE event SET event_id = ((event_id)::int - 50000)::varchar(5)")
            await db.execute(f"DELETE FROM event WHERE (event_id::int) <= 0")

async def edit_event_field(bot, message):
    '''|user|
    (Bot object, Message object) -> None

    Format:  <prefix> edit event <id> <subcommand field> <args>
    Command: <prefix>edit event <id> name <text> ...
    Command: <prefix>edit event <id> description <text> ...
    Command: <prefix>edit event <id> instruction <text> ...
    Command: <prefix>edit event <id> start <yyyy>/<mm>/<dd> <hh>:<mm>
    Command: <prefix>edit event <id> finalize

    Checks:
    -Message author's rank sufficient
    -event.finalized = False
    -subcommand field

    Actions: -calls edit_event_text/start/finalize() based on subcommand field.
    '''
    command_opener = 'edit event'
    if message.content.startswith(command_opener):
        print('editing event...')
        msg = message.content.split()[2:]
        event_id = msg[0]
        if event_id.isdigit() and (await db.user_has_permission(message.author.id, command_opener) or await db.is_event_host(message.author.id)):
            if await db.event_finalized(event_id):
                await bot.send_message(message.author, "Error: cannot edit a finalized event.")
            else:
                field = msg[1]
                if field in ['name', 'description', 'instruction']:
                    await edit_event_text(bot, message, command_opener)
                elif field == 'start':
                    await edit_event_start(bot, message, command_opener)
                elif field == 'finalize':
                    await edit_event_finalize(bot, message, command_opener)

async def edit_event_text(bot, message, command_opener):
    '''|user|
    (Bot object, Message object) -> None

    Command: <prefix>edit event <id> <name/description/instruction> <text>

    Invoked: edit_event_field() after checking:
    -message author's rank
    -event.finalized = False

    Actions: -alters event name, description, or instruction to the specified text.
    '''
    print('editing event name/description/instruction...')
    msg = message.content.split()
    event_id = msg[2]
    field = msg[3]
    text = ' '.join(msg[4:])
    try:
        await db.execute(f"UPDATE event SET {field} = $1 WHERE event_id = $2", text, event_id)
    except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
    else: await bot.send_message(message.author, f'Event #{event_id} {field} set to "{text}".')

async def edit_event_start(bot, message, command_opener):
    '''|user|
    (Bot object, Message object) -> None

    Command: <prefix>edit event <id> start <yyyy>/<mm>/<dd> <hh>:<mm>

    Invoker: edit_event_field() after checking:
    -message author's rank
    -event.finalized = False

    Actions: 
    -alters event starts_at to the specified date and time.
    -assume Pacific, Canada time zone until further implementation.
    '''
    print('editing event start...')
    msg = message.content.split()
    event_id = msg[2]
    date = msg[4].split('/')
    time = msg[5].split(':')
    dt_arr = list(map(int, date + time))
    start = datetime.datetime(year = dt_arr[0], month= dt_arr[1], day = dt_arr[2], hour = dt_arr[3], minute = dt_arr[4])
    try: await db.execute(f"UPDATE event SET starts_at = $1 WHERE event_id = $2", start, event_id)
    except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
    else: await bot.send_message(message.author, f'Event #{event_id} starting datetime set to {msg[4]} {msg[5]} Pacific.')

async def edit_event_finalize(bot, message, command_opener):
    '''|user|
    (Bot object, Message object, str) -> None

    Command: <prefix>edit event <id> finalize

    Invoker: edit_event_field() after checking:
    -message author's rank
    -event.finalized = False

    Given: -event_id, message.author.id
    Checks: -event.name, .description, .instruction, .starts_at are not null. 
    Action: sets event.finalized to True, preventing further edit command calls for this event.
    '''
    print('finalizing event...')
    msg = message.content.split()
    event_id = msg[2]
    try:
        records_list = await db.fetch(f"SELECT * FROM event WHERE event_id = $1", event_id)
        records_dict = rd = records_list[0]
        if rd['name'] and rd['description'] and rd['instruction'] and rd['starts_at']:
            field_empty_error = False
            await db.execute(f"UPDATE event SET finalized = TRUE WHERE event_id = $1", event_id)
        else:
            field_empty_error = True
    except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
    else:
        if field_empty_error:
            await bot.send_message(message.author, "Event must have name, description, instruction, and start time to be finalized.")
        else:
            await spawn_reminder_entries(event_id, rd['starts_at'], bot)
            await bot.send_message(message.author, f'Event #{event_id} finalized.')

async def spawn_reminder_entries(event_id, starts_at, bot):
    '''|bot|
    (str, datetime.datetime object) -> None

    Invoker: -edit_event_finalize() when event is finalized.
    Given: -event id, intended start time
    Action: -inserts 9 new entries of varying reminder times for the event into bot.reminders table.
    '''
    #debug
    success = False
    print('spawning reminder entries...')
    b12h = starts_at - datetime.timedelta(hours=12)
    b6h = starts_at - datetime.timedelta(hours=6)
    b1h = starts_at - datetime.timedelta(hours=1)
    b30m = starts_at - datetime.timedelta(minutes=30)
    b10m = starts_at - datetime.timedelta(minutes=10)
    b2m = starts_at - datetime.timedelta(minutes=2)
    a5m = starts_at + datetime.timedelta(minutes=5)
    a10m = starts_at + datetime.timedelta(minutes=10)
    a15m = starts_at + datetime.timedelta(minutes=15)
    description_arr = list(map(lambda x: x[1:] + ' before' if x[0] is 'b' else x[1:] + ' after', 'b12h b6h b1h b30m b10m b2m a5m a10m a15m'.split()))
    description_to_dt = list(zip(description_arr, [b12h, b6h, b1h, b30m, b10m, b2m, a5m, a10m, a15m]))
    for description, dt in description_to_dt:
        try: await db.execute(f"INSERT INTO reminders (reason, reason_id, description, due, subscribers) VALUES ('event', $1, $2, $3, $4)", event_id, description, dt, [])
        except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
        else: success = True
    if success: 
        await bot.send_message(secrets.bot_owner, f'Reminders for event #{event_id} spawned.')
        await reminder.reminder_checker(bot)
           
async def event_rvsp(bot, message):
    '''|user|
    Command: <prefix>rvsp event <id> <yes>
    Command: <prefix>rvsp event <id> <no>

    Given: -event id, message author
    Checks: -event.archived = False
    Action: -inserts new entry into bot.rvsp for user for this event if none exists, updates entry otherwise
    with 'yes' or 'no', allowing user to express if they will be attending that event.
    '''
    command_opener = 'event rvsp'
    errors = ''
    success = False
    if message.content.startswith(command_opener):
        print('rvsping to event...')
        if await db.user_has_permission(message.author.id, command_opener):
            msg = message.content.split()[2:]
            event_id = msg[0]
            answer = msg[1]
            if answer in ['yes', 'no']:
                #jump
                answerdict = {'yes': True, 'no': False}
                #--- see if there is an entry for this user and event already
                try:
                    records_list = await db.fetch("SELECT * FROM rvsp WHERE event_id = $1 AND user_id = $2", event_id, message.author.id)
                except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
                else:
                    #--- if entry already exists
                    if records_list:
                        old_answer = records_list[0]['will_attend']
                        if old_answer != answer:
                            try: await db.execute("UPDATE rvsp SET will_attend = $1 WHERE user_id = $2", answerdict[answer], message.author.id)
                            except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
                            else: success = True
                    #--- if no such entry exists
                    else:
                        try: await db.execute("INSERT INTO rvsp (event_id, user_id, will_attend) VALUES ($1, $2, $3)", event_id, message.author.id, answerdict[answer])
                        except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
                        else: success = True
            #--- answer was not 'yes' or 'no'
            else:
                errors += f'Accepted commands are:\n{secrets.prefix}rvsp event <id> yes\n{secrets.prefix}rvsp event <id> no\n'
        #--- user has insufficient rank
        else:
            errors += 'You do not have permission to use this command.\n'
        #--- if there are error messages to deliver to user
        if errors:
            await bot.send_message(message.author, f"Error:\n{errors}")
        #--- if successful
        elif success:
            await bot.send_message(message.author, f'RVSP status for event#{event_id} updated to "{answer}". Thank you for your response.')

async def set_reminder(bot, message):
    '''|user|
    (Bot object, Message object) -> None

    Command: <prefix>set reminder <reason_id>

    Given: -reason id, message author
    Checks: -message author rank, reason.finalized = True
    Actions: 
    -allows user to subscribe to existing reminders
    -shows user a 'menu' of reminders available for the event and allows user to choose several
    '''
    command_opener = 'set reminder'
    errors = ''
    success = False
    if message.content.startswith(command_opener):
        print('setting reminders...')
        if await db.user_has_permission(message.author.id, command_opener):
            msg = message.content.split()[2:]
            reason_id = msg[0]
            #--- check if reminders exist for this reason
            try: list_of_reminders = await db.fetch("SELECT * FROM reminders WHERE reason_id = $1", reason_id)
            except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
            else:
                #--- if such reminders exist
                if list_of_reminders:
                    reason_type = list_of_reminders[0]['reason']
                    #--- show all reminders as a menu for user and whether they've subscribed
                    #--- for every selected option, append them to subscribers list
                    #--- for every unselected option, remove them from subscribers list
                    alphabet_list = list(string.ascii_lowercase)[:len(list_of_reminders)]
                    alphabet_to_reminder = dict(zip(alphabet_list, list_of_reminders))
                    menu = '```'
                    menu += f" {'option':^8} | {'description':^13} | {'subscribed?':^13}\n"
                    for alphabet, reminder in alphabet_to_reminder.items():
                        option = alphabet
                        reminder_description = reminder['description']
                        reminder_subscribers = reminder['subscribers']
                        subscribed = 'Y' if message.author.id in reminder_subscribers else 'N'
                        menu += f" {option:^8} | {reminder_description:^13} | {subscribed:^13}\n"
                    menu += '```'
                    await bot.send_message(message.author, f"The following are reminder/alarms you can subscribe to for {reason_type}#{reason_id}. I will privately message you reminding you about the {reason_type} at the subscribed times.\n{menu}\n\nReply with all options you wish to subscribe to in one comment, separated by spaces.\nOptions not mentioned will be unsubscribed from.\nFor example: a d e")
                    reply = await bot.wait_for_message(author=message.author, timeout=30)
                    if reply:
                        reply = reply.content
                        if ' ' in reply:
                            replies = reply.split()
                        else:
                            replies = [letter for letter in reply]
                        try:
                            for alphabet, reminder in alphabet_to_reminder.items():
                                subscribers_list = reminder['subscribers']
                                if alphabet in replies:
                                    if message.author.id not in subscribers_list:
                                        subscribers_list.append(message.author.id)
                                        print(f'subscribers_list = {subscribers_list}')
                                        print(f'reason_id = {reason_id}')
                                        print(f"reminder['description'] = {reminder['description']}\n")
                                        await db.execute("UPDATE reminders SET subscribers = $1 WHERE reason_id = $2 AND description = $3", subscribers_list, reason_id, reminder['description'])
                                else:
                                    if message.author.id in subscribers_list:
                                        subscribers_list.remove(message.author.id)
                                        await db.execute("UPDATE reminders SET subscribers = $1 WHERE reason_id = $2 AND description = $3", subscribers_list, reason_id, reminder['description'])
                        except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
                        else: success = True
                    else:
                        await bot.send_message(message.author, "Feel free to have some time to think about it, just call me again when you're ready.")
                #--- if reminders don't exist
                else:
                    errors == 'No reminders/alarms available for the reason/event you provided.\n'
       #--- user has insufficient rank
        else:
            errors += 'You do not have permission to use this command.\n'
        if success:
            await bot.send_message(message.author, "Reminders updated. Thank you.")

async def event_list(bot, message):
    '''|user|
    (Bot object, Message object) -> None
    
    Command: <prefix>event list *
    Command: <prefix>event list <event_id> <event_id> ...
    
    Checks: -message author rank, event_id active if given
    Action: fetches only active events and displays details to message author.
    ''' 
    command_opener = 'event list'
    errors = ''
    success = False
    valid_ids = False
    if message.content.startswith(command_opener):
        print('listing events...')
        if await db.user_has_permission(message.author.id, command_opener):
            msg = message.content.split()[2:]
            text = 'Current events:\n\n'
            #--- if asking to list all entries
            if len(msg) == 1 and msg[0] == '*':
                print('fetching all event entries...')
                rl = await db.fetch(f"SELECT u.nickname, e.event_id, e.name, e.description, e.instruction, e.starts_at FROM user_objects u, event e WHERE e.host_id = u.id AND e.finalized = 't' AND e.archived = 'f' ORDER BY e.event_id ASC")
                if rl:
                    for r in rl: #list of multiple records
                        text += f"#{r['event_id']} {r['name']} | {r['starts_at']} PDT | hosted by: {r['nickname']}\n```{r['description']}\n{r['instruction']}```\n\n"
                    valid_ids = True 
                    success = True

            #--- if asking to list specific entries
            elif len(msg) >= 1 and all_elements_are_len(msg, 5):
                print('fetching specified event entries...')
                ids_to_fetch = msg
                for eid in ids_to_fetch:
                    try: rl = await db.fetch(f"SELECT u.nickname, e.event_id, e.name, e.description, e.instruction, e.starts_at FROM user_objects u, event e WHERE e.host_id = u.id AND e.finalized = 't' AND e.archived = 'f' AND e.event_id = $1",  eid)
                    except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
                    else:
                        if rl: #list of one record
                            valid_ids = True
                            success = True
                            r = rl[0]
                            text += f"#{r['event_id']} {r['name']} | {r['starts_at']} PDT | hosted by: {r['nickname']}\n```{r['description']}\n{r['instruction']}```\n\n"  

            #--- if neither format
            else: errors += f'Incorrect format.\nMust be either `{secrets.prefix}event list *` or `{secrets.prefix}event list <event_id> <optionally more event_ids separated by spaces>`.\n\nEvent_id must be 5 digits long.'
        else: errors += "You do not have permission to use this command.\n\n"
        if not valid_ids: errors += f'No valid event ids supplied. Try `{secrets.prefix}event list *` to list all current events.'
        if errors: await bot.send_message(message.author, f'Error:\n{errors}')
        elif success: await bot.send_message(message.author, text)

def all_elements_are_len(arr, leng):
    '''|bot|
    (list, integer) -> bool

    Action: return True if all elements in array are exactly leng length, False otherwise.
    '''
    for element in arr:
        if len(element) != leng:
            return False
    return True

