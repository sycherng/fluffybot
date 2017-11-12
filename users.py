import db
import main
import math

async def respond(bot, message):
    rank = await get_rank(message.author.id) 
    if rank in ['owner', 'admin']:
        await manual_signup(message)
        await manual_change_balance(message)
        await manual_set_balance(message)

#--- F E T C H / C H E C K---#
async def get_nickname(user_id):
    x = db.fetch("SELECT nickname FROM user_log WHERE user_id = '{}';".format(user_id))
    return x[0][0]

async def get_rank(user_id):
    x = db.fetch("SELECT rank FROM user_log WHERE user_id = '{}';".format(user_id))
    return x[0][0]

async def get_balance(user_id):
    x = db.fetch("SELECT balance FROM user_log WHERE user_id = '{}';".format(user_id))
    return x[0][0]

async def get_sticker_allowance(user_id):
    x = db.fetch("SELECT sticker_allowance FROM user_log WHERE user_id = '{}';".format(user_id))
    return x[0][0]

#--- C H A N G E / S E T ---#
async def set_nickname(user_id, new_nickname):
async def set_rank(user_id, new_rank):
async def set_balance(user_id, new_balance):
    db.update("UPDATE user_log SET balance = {} WHERE user_id = '{}';".format(new_balance, user_id))

async def set_sticker_allowance(user_id, new_quantity):
async def ch_balance(user_id, delta):
    current_balance = get_balance(user_id)
    new_balance = current_balance + delta
    db.update("UPDATE user_log SET balance = {} WHERE user_id = '{}';".format(new_balance, user_id))

async def reset_sticker_allowance():

#--- S I G N U P ---#
async def does_user_exist(ion):
    x = db.fetch("SELECT * FROM user_log WHERE user_id = '{}';".format(ion))
    if x != []:
        return True
    y = db.fetch("SELECT * FROM user_log WHERE nickname = '{}';".format(ion))
    if y != []:
        return True
    return False

async def auto_signup(user):
    if not await does_user_exist(user.id):
        user_id = user.id
        nickname = user.name
        await create_new_user(user_id, nickname)

async def manual_signup(message):
    text = message.content.split()
    if text[0] == 'mk' and text[1] == 'user' and len(text) == 4:
            user_id = text[2]
            nickname = text[3]
            if await main.verid(user_id):
                await create_new_user(bot, user_id, nickname)

async def create_new_user(user_id, nickname):
    if not await does_user_exist(user_id):
        db.update("INSERT INTO user_log (user_id, nickname) VALUES('{}', '{}');".format(user_id, nickname))

#--- B A L A N C E ---#
async def str_is_signum_int(ss):
    if ss.startswith('-') or ss.startswith('+'):
        try:
            int(ss[1:])
        except:
            return False
        else:
            return True
    return False

async def signumintstr_to_int(ss):
    """accepts +5 -5, returns 5, -5"""
    integer = int(ss[1:])
    signum = ss[0]
    if signum == '-':
        return -1 * integer
    else:
        return integer

async def manual_change_balance(message):
    text = message.content.split()
    if text[0]=='ch' and text[1]=='bal' and len(text) == 4:
        delta = text[3]
        user_id = text[2]
        if does_user_exist(user_id) and await str_is_signum_int(delta):
            delta = await signumintstr_to_int(delta)
            await change_balance(user_id, delta)

async def manual_set_balance(message):
    text = message.content.split()
    if text[0]=='set' and text[1]=='bal' and len(text) == 4:
        balance = text[3]
        user_id = text[2]
        if does_user_exist(user_id) and await str_is_signum_int(balance):
            balance = await signumintstr_to_int(balance)
            await set_balance(user_id, balance)
#---
