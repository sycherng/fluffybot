import asyncio, datetime
import async_db as db, secrets
import user

async def respond(bot, message):
    pass

async def prefix_respond(bot, message):
    await create_event(bot, message)
    await edit_event_field(bot, message)

async def create_event(bot, message):
    '''|user|
    (Bot object, Message object) -> None

    Command: <prefix>create event

    Creates an event entry in bot's database if message author has sufficient rank with bot.
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

    Checks below critera before invoking edit_event_text/start/finalize():
    -Message author's rank sufficient
    -event.finalized = False
    -subcommand field
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

    Command: <prefix>edit event <id> <name/description/instruction> <value>

    Alters event field to new value if message author has sufficient rank with bot.
    Valid fields are 'name', 'description' and 'instruction'.

    Before this function is invoked, the following qualifications are checked by edit_event_field():
    - Message author's rank sufficient
    - event.finalized = False
     '''
    msg = message.content.split()
    event_id = msg[2]
    field = msg[3]
    value = ' '.join(msg[4:])
    try:
        await db.execute(f"UPDATE event SET {field} = $1 WHERE event_id = $2", value, event_id)
    except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)
    else: await bot.send_message(message.author, f'Event #{event_id} {field} set to "{value}".')

async def edit_event_start(bot, message, command_opener):
    '''|user|
    (Bot object, Message object) -> None

    Command: <prefix>edit event <id> start <yyyy>/<mm>/<dd> <hh>:<mm>

    Alters event's starts_at field to new value if message author has sufficient rank with bot.
    All times will be in Pacific, Canada zone until further implementation.

    Before this function is invoked, the following qualifications are checked by edit_event_field():
    - Message author's rank sufficient
    - event.finalized = False
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

    Given event_id, checks if event.name, .description, .instruction, .starts_at are not null. If 
    satisfied, sets event.finalized to True, thus disabling future edit commands from being performed
    on this event.

    Before this function is invoked, the following qualifications are checked by edit_event_field():
    - Message author's rank sufficient
    - event.finalized = False
    '''
    msg = message.content.split()
    event_id = msg[2]
    try:
        records_list = await db.fetch(f"SELECT * FROM event WHERE event_id = $1", event_id)
        records_dict = rd = records_list[0]
        if rd['name'] and rd['description'] and rd['instruction'] and rd['starts_at']:
            await db.execute(f"UPDATE event SET finalized = TRUE WHERE event_id = $1", event_id)
            await bot.send_message(message.author, f'Event #{event_id} finalized.') 
        else:
            await bot.send_message(message.author, "Event must have name, description, instruction, and start time to be finalized.")
    except Exception as error: await user.notify_owner(bot, command_opener, message.author, error)

