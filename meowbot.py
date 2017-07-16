import discord
import asyncio
from discord.ext.commands import Bot

bot = Bot (command_prefix="!")
bot_token = "MzEyMDI1Mzk1NTI2MzY5Mjgw.C_VD6g.zIegrIoqWJ2i4ajuvgX-CyRqyQc"
bot_name = 'Meow-bot'
cmd_opener = 'mw'
id_straw = '***REMOVED***'

@bot.event
async def on_ready():
    await bot.edit_profile(username=bot_name)
    print(bot_name + " logged in via bot_main.py\n------")
    await bot.send_message(discord.User(id = id_straw), bot_name +" logged in.")

@bot.event
async def on_message(message):
    if message.author.id != '312025395526369280':
        if message.author.id == id_straw:
            if message.content.startswith(cmd_opener):
                msg = message.content
                msg = msg.split(cmd_opener)
                msg = "".join(msg)
                await bot.send_message(message.channel, msg)

bot.run(bot_token)
