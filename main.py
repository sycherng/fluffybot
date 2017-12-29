import discord, asyncio
from discord.ext.commands import Bot
import datetime
import secrets, db, user, welcome

bot = Bot(command_prefix = secrets.prefix)

@bot.event
async def on_ready():
    print(secrets.bot_name + ' logged in.\n------')
    await bot.send_message(secrets.bot_owner, 'Logged in via ' + __file__ + '. Ready for action!')

@bot.event
async def on_message(message):
    if message.author.id != secrets.bot_discord_id: #---Do not listen to self, do not accept any queries with the word table
        print('main 0')
        await user.spawn_user(bot, message) #---Auto add everyone to db.user_table table
        await welcome.submit_my_response(bot, message)
        if message.content.startswith(secrets.prefix) and db.check(message.author.id, 'rank', db.users) != 'alien':
            print('main 1') 
            message.content = message.content[1:] #---Slice off command prefix
            await copy_to_echo_room(message) #---paste to echo room for troubleshooting
            await user.respond(bot, message) #---send to modules
            await welcome.respond(bot, message)

async def copy_to_echo_room(message):
    await bot.send_message(secrets.echo_room, '{}/{}/{}/{}'.format(get_timestamp(), message.channel, message.author, message.content))

def get_timestamp():
    now = datetime.datetime.now()
    year = str(now.year)
    month = str(now.month)
    day = str(now.day)
    hour = str(now.hour)
    minute = str(now.minute)
    second = str(now.second)
    timestamp = '{}-{}-{} {}:{}:{}'.format(year, month.zfill(2), day.zfill(2), hour.zfill(2), minute.zfill(2), second.zfill(2))
    return timestamp

if __name__ == '__main__':
    bot.run(secrets.bot_token)
 
