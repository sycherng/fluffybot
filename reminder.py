import discord, asyncio, datetime
import async_db as db
import secrets

'''
look in reminder table with time sorted ascending and time period within now and 5 minutes from now
pull the reason, reason_id, description, and subscribers to message all subscribers with "Pokey, this is a reminder that reason reason_id taking place in description."
'''
async def respond(bot, message):
    if message.content == 'debug reminder checker':
        await reminder_checker(bot)

async def prefix_respond(bot, message):
    pass

async def reminder_checker(bot):
    await bot.wait_until_ready()
    print('initiating reminder checker...')
    while not bot.is_closed:
        print('checking reminders')
        now = datetime.datetime.now()
        then = now + datetime.timedelta(minutes=5)
        try: records_list = await db.fetch("SELECT * FROM reminders WHERE due > $1 and due < $2", now, then)
        except Exception as error: await bot.send_message(secrets.bot_owner, f"Reminder checker failed to fetch reminders at {now}.\nError:\n```{error}```")
        else:
            if records_list:
                for record in records_list:
                    subscribers = record['subscribers'] #list of ids
                    if subscribers:
                        reason = record['reason']
                        reason_id = record['reason_id']
                        description = record['description'].split()
                        for subscriber in subscribers:
                            if description[1] == 'after':
                                await bot.send_message(discord.User(id=subscriber), f"Pokey, this is a reminder for {reason} #{reason_id}\nIt started {description[0]} ago.")
                            elif description[1] == 'before':
                                await bot.send_message(discord.User(id=subscriber), f"Pokey, this is a reminder for {reason} #{reason_id}\nIt is taking place in {description[0]}.")
        await asyncio.sleep(5*60) 
