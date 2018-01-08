import asyncio
import async_db as db, secrets
import user

async def respond(bot, message):
    pass

async def prefix_respond(bot, message):
    await create_event(bot, message)


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

#have a reminder setup process with the bot
