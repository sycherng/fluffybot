import db
import main
import math

async def respond(bot, message):
    await auto_signup(message.author)    
    await manual_signup(bot, message)
    await manual_change_balance(bot, message)
    await manual_set_balance(bot, message)

async def does_user_exist(user_id):
    x = db.fetch("select * FROM user_log WHERE user_id = '{}';".format(user_id))
    if x == []:
        return False
    return True

async def auto_signup(user):
    if not await does_user_exist(user.id):
        user_id = user.id
        nickname = user.name
        await create_new_user(user_id, nickname)

async def manual_signup(bot, message):
    text = message.content.split()
    if text[0] == 'mk' and text[1] == 'user' and len(text) == 4:
            user_id = text[2]
            nickname = text[3]
            if await main.verid(user_id):
                await create_new_user(user_id, nickname)
    else:
        await main.chide(bot, message, 'mk user <id> <nickname>')

async def create_new_user(user_id, nickname):
    if not await does_user_exist(user_id):
        db.update("INSERT INTO user_log (user_id, nickname) VALUES('{}', '{}');".format(user_id, nickname))

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

async def manual_change_balance(bot, message):
    text = message.content.split()
    if text[0]=='ch' and text[1]=='bal' and len(text) == 4:
        delta = text[3]
        user_id = text[2]
        if await str_is_signum_int(delta):
            delta = await signumintstr_to_int(delta)
            await change_balance(user_id, delta)
    else:
        await main.chide(bot, message, 'ch bal <id> <+/-><integer>')

async def change_balance(user_id, delta):
    x = db.fetch("SELECT balance FROM user_log WHERE user_id = '{}';".format(user_id))
    current_balance = x[0][0]
    new_balance = current_balance + delta
    db.update("UPDATE user_log SET balance = {} WHERE user_id = '{}';".format(new_balance, user_id))

async def manual_set_balance(bot, message):
    text = message.content.split()
    if text[0]=='set' and text[1]=='bal' and len(text) == 4:
        bal = text[3]
        user_id = text[2]
        if await str_is_signum_int(bal):
            bal = await signumintstr_to_int(bal)
            await set_balance(user_id, bal)
    else:
        await main.chide(bot, message, 'set bal <id> <+/->integer')

async def set_balance(user_id, bal):
    db.update("UPDATE user_log SET balance = {} WHERE user_id = '{}';".format(bal, user_id))

async def fetch_members():
    x = db.fetch("SELECT * FROM user_log WHERE user_id != 'alien';")
    
