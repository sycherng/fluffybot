import discord, asyncio
from discord.ext.commands import Bot
import datetime
import secrets, db, user

#---client
bot_token, bot_discord_id  = secrets.bot_token, secrets.bot_discord_id
bot = Bot(command_prefix = '=')

#--- external settings
bot_name, prefix = 'Fluffy-bot', '='
currency_name = 'waifu bucks'
echo_room = discord.Object(id = '366306796727566336')
bot_owner = discord.User(id = '***REMOVED***')

@bot.event
async def on_ready():
    print(bot_name + ' logged in.\n------')
    await bot.send_message(bot_owner, 'Logged in via ' + __file__ + '. Ready for action!')

@bot.event
async def on_message(message):
    if message.author.id != bot_discord_id: #---Do not listen to self, do not accept any queries with the word table
        print('main 0')
        await user.spawn_user(bot, message) #---Auto add everyone to db.user_table table
        if message.content.startswith(prefix) and db.check(message.author.id, 'rank', db.users) != 'alien':
            print('main 1') 
            message.content = message.content[1:] #---Slice off command prefix
            await copy_to_echo_room(message) #---paste to echo room for troubleshooting
            await user.respond(bot, message) #---send to modules

async def copy_to_echo_room(message):
    await bot.send_message(echo_room, '{}/{}/{}/{}'.format(get_timestamp(), message.channel, message.author, message.content))

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
    bot.run(bot_token)
