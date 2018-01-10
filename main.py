import discord, asyncio
from discord.ext.commands import Bot
import datetime

#import custom test modules for experimental code
from examples import test
from examples.dupe import *
#import custom modules which do not interact with users
import secrets, async_db as db

#import custom modules which interact with users
import user, welcome, event

bot = Bot(command_prefix = secrets.prefix)

@bot.event
async def on_ready():
    print(secrets.bot_name + ' logged in.\n------')
    await bot.send_message(secrets.bot_owner, 'Logged in via ' + __file__ + '. Ready for action!')

@bot.event
async def on_message(message):
    #--- ignore self
    if message.author.id != secrets.bot_discord_id:
        #--- debugging messages
        print(f'{message.author}: {message.content}')
        await copy_to_echo_room(message)

        #--- spawn any new users in user_objects
        await user.spawn_user(message)

        #--- forward message to test.py module
        await test.respond(bot, message)

        #--- aliens not permitted to use
        if await db.get_rank(message.author.id) != 'alien':
            #---forward message to prefixed (command) functions of all other modules
            if message.content.startswith(secrets.prefix):
                #---Slice off command prefix
                message.content = message.content[1:]
                await user.prefix_respond(bot, message) 
                await welcome.prefix_respond(bot, message)
                await event.prefix_respond(bot, message)

            #--- forward message to non-prefixed functions of all other modules
            else:
                await user.respond(bot, message)
                await welcome.respond(bot, message)
                await event.respond(bot, message)


async def copy_to_echo_room(message):
    await bot.send_message(secrets.echo_room, f'`{get_timestamp()}/{message.channel}/{message.author.name[:-5]} {message.author.id}`\n```{message.content}```')

def get_timestamp():
    now = datetime.datetime.now()
    year = str(now.year)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)
    hour = str(now.hour).zfill(2)
    minute = str(now.minute).zfill(2)
    second = str(now.second).zfill(2)
    timestamp = f'{year}-{month}-{day} {hour}:{minute}:{second}'
    return timestamp

if __name__ == '__main__':
    bot.run(secrets.bot_token)
 
