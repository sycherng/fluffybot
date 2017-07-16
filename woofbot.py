import discord
import asyncio
from discord.ext.commands import Bot

bot = Bot (command_prefix="!")
bot_token = "MzEyMDI0NjUwNzM1NjgxNTM4.C_VDkA.76k5kZwMEnFe-eDS40t_5QQoRuo"
bot_name = 'Woof-bot'
cmd_opener = 'wf'
id_straw = '***REMOVED***'

@bot.event
async def on_ready():
    await bot.edit_profile(username=bot_name)
    print(bot_name + " logged in via bot_main.py\n------")
    await bot.send_message(discord.User(id = id_straw), bot_name + " logged in.")

@bot.event
async def on_message(message):
    if message.author.id != '312024650735681538':
        if message.author.id == id_straw:
            if message.content.startswith(cmd_opener):
                msg = message.content
                msg = msg.split(cmd_opener)
                msg = "".join(msg)
                await bot.send_message(message.channel, msg)

bot.run(bot_token)
