import asyncio, datetime
import async_db as db, secrets
import user

async def respond(bot, message):
    pass

async def prefix_respond(bot, message):
    await create_event(bot, message)
    await edit_event_field(bot, message)
    await event_rvsp(bot, message)
    await set_reminder(bot, message)

async def create_event(bot, message):
    '''|user|
    (Bot object, Message object) -> None

    Command: <prefix>create event

    Checks: message author rank
    Actions: creates an event object represented by a new entry in bot's "event" table.
    '''
    command_opener = 'create event'
    if message.content == command_opener and await db.user_has_permission(message.author.id, command_opener):
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

    Invoked: edit_event_field() after checking:
    -message author's rank
    -event.finalized = False

    Actions: 
    -alters event starts_at to the specified date and time.
    -assume Pacific, Canada time zone until further implementation.
    '''
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
    msg = message.content.split()
    event_id = msg[2]
    try:
        records_list = await db.fetch(f"SELECT * FROM event WHERE event_id = $1", event_id)
        records_dict = rd = records_list[0]
        if rd['name'] and rd['description'] and rd['instruction'] and rd['starts_at']:
            field_empty_error = False
            await db.execute(f"UPDATE event SET finalized = TRUE WHERE event_id = $1", event_id)
            await spawn_reminder_entries(event_id, rd['starts_at'])
       else:
            field_empty_error = True
    except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
    else:
        if field_empty_error:
            await bot.send_message(message.author, "Event must have name, description, instruction, and start time to be finalized.")
        else:
            await bot.send_message(message.author, f'Event #{event_id} finalized.')

async def spawn_reminder_entries(event_id, starts_at):
    '''|bot|
    (str, datetime.datetime object) -> None

    Invoker: -edit_event_finalize() when event is finalized.
    Given: -event id, intended start time
    Action: -inserts 9 new entries of varying reminder times for the event into bot.reminders table.
    '''
    b12h = starts_at - datetime.timedelta(hours=12)
    b6h = starts_at - datetime.timedelta(hours=6)
    b1h = starts_at - datetime.timedelta(hours=1)
    b30m = starts_at - datetime.timedelta(minutes=30)
    b10m = starts_at - datetime.timedelta(minutes=10)
    b2m = starts_at - datetime.timedelta(minutes=2)
    a5m = starts_at + datetime.timedelta(minutes=5)
    a10m = starts_at + datetime.timedelta(minutes=10)
    a15m = starts_at + datetime.timedelta(minutes=15)
    for tup in zip('b12h b6h b1h b30m b10m b2m a5m a10m a15m'.split(), [b12h, b6h, b1h, b30m, b10m, b2m, a5m, a10m, a15m]):
        for title, dt in tup:
            await db.execute(f"INSERT INTO reminders (reason, reason_id, name, due, subscribers) VALUES ('event', {event_id}, {title}, {dt}, [])")
    await bot.send_message(secrets.bot_owner, f'Reminders for event #{event_id} spawned.')
           
async def event_rvsp(bot, message, command_prefix):
    '''|user|
    Command: <prefix>rvsp event <id> <yes>
    Command: <prefix>rvsp event <id> <no>

    Given: -event id, message author
    Checks: -event.archived = False
    Action: -inserts new entry into bot.rvsp for user for this event if none exists, updates entry otherwise
    with 'yes' or 'no', allowing user to express if they will be attending that event.
    '''
    command_prefix = 'event_rvsp'
    errors = ''
    if message.content.startswith('event rvsp'):
        if await db.user_has_permission(message.author.id, command_prefix):
            msg = message.content.split()[2:]
            event_id = msg[0]
            answer = msg[1]
            if answer == 'yes':
                #jump
                try: records_list = 
                except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
                

            elif answer == 'no':
                try:
                except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
                
            else:
                errors += f'Accepted commands are:\n{secrets.prefix}rvsp event <id> yes\n{secrets.prefix}rvsp event <id> no\n'
        else:
            errors += 'You do not have permission to use this command.\n'
        if errors:
            await bot.send_message(message.author, f"Error:\n{errors}")
        else:
            await bot.send_message(message.author, f'RVSP status for event#{event_id} updated to "{answer}". Thank you for your response.')

async def set_reminder(bot, message):
    '''|user|
    (Bot object, Message object) -> None

    Command: <prefix>set reminder <reason_id> <a b c d e>

    Given: -reason id, message author
    Checks: -message author rank, reason.finalized = True
    Action: -allows user to subscribe to existing reminders
    '''

   
