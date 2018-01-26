import discord
import asyncio
import secrets
from discord.ext.commands import Bot

#---initialize bot values
sec = secrets.Secrets(2)
bot_token = sec.token
bot_id = sec.discord_id
bot_name = sec.name
builtin_prefix = sec.builtin_prefix
custom_prefix = sec.custom_prefix

bot = Bot(command_prefix=builtin_prefix)

@bot.event
async def on_ready():
    await bot.edit_profile(username=bot_name)
    print(f"{bot_name} logged in via {__name__}.")
    await bot.send_message(secrets.bot_owner, f"{bot_name} logged in.")

@bot.event
async def on_message(message):
    if message.author.id != bot_id and message.author.id == secrets.bot_owner and message.content.startswith(custom_prefix):
        await echoCommand(bot, message)

async def echoCommand(bot, message):
    msg = message.content
    msg = msg.split(cmd_opener)
    msg = "".join(msg)
    await bot.send_message(message.channel, msg)

bot.run(bot_token)
