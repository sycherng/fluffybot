import discord, asyncio, random
import async_db as db, secrets
import user

async def respond(bot, message):
    '''messages that came in without prefix in front'''
    pass

async def prefix_respond(bot, message):
    '''messages that came in with prefix in front'''
    pass

async def user_welcome(bot, message):
    helptext = f'''
    |user|
    Command: {secrets.prefix}user welcome +game <user_id>
    Command: {secrets.prefix}user welcome <user_id>
    '''
    '''
    Checks: -message author rank, target exists in user_objects database
    Action: 
    -spawns welcome entry in database for target
    -delivers a welcome message for the user in channel shared by all members
    -if +game, delivers message in the form of 2 truths 1 wish minigame
    '''
    command_opener = 'user welcome'
    if not message.content.startswith(command_opener): return
    if not await db.user_has_permission(message.author.id, command_opener): return
    msg = message.content[2:]
    #---validate command
    if len(msg) == 2 and msg[0] == '+game' and await db.is_valid_id(msg[1]):
        game = True
        target_id = msg[1]
    elif len(msg) == 1 and await db.is_valid_id(msg[0]):
        game = False
        target_id = msg[0]
    else:
        await bot.send_message(message.author, f"Error: invalid format.\n\n```{helptext}```")
    #---validate target  existence
    if not db.user_exists(target_id):
        await bot.send_message(message.author, f"Error, user does not exist in database. Create user first.")
        return
    #---acquire target details
    
    await bot.send_message(message.author, "Which category best describes the new member?\n")

    #---if no game
    if not game: await user_welcome_no_game(bot, message):
    #---if game
     

