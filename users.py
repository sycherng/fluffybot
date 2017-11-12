import db
import main
import math

async def respond(bot, message):
    rank = await get_rank(message.author.id) 
    if rank == 'member':
        await request_my_profile(bot, message)
        await request_specific_profile(bot, message)
        await request_all_profiles(bot, message)
    if rank == 'owner' or rank == 'admin':
        await manual_signup(message)
        await manual_change_balance(message)
        await manual_set_balance(message)
    if rank == 'owner':
        await manual_reset_stickers(message)

#--- F E T C H / C H E C K---#
async def get_nickname(user_id):
    if await does_user_exist(user_id):
        x = db.fetch("SELECT nickname FROM user_log WHERE user_id = '{}';".format(user_id))
        return x[0][0]

async def get_rank(user_id):
    if await does_user_exist(user_id):
        x = db.fetch("SELECT rank FROM user_log WHERE user_id = '{}';".format(user_id))
        return x[0][0]

async def get_balance(user_id):
    if await does_user_exist(user_id):
        x = db.fetch("SELECT balance FROM user_log WHERE user_id = '{}';".format(user_id))
        return x[0][0]

async def get_sticker_allowance(user_id):
    if await does_user_exist(user_id):
        x = db.fetch("SELECT sticker_allowance FROM user_log WHERE user_id = '{}';".format(user_id))
        return x[0][0]

async def get_user_profile(user_id):
    if await does_user_exist(user_id):
        x = db.fetch("SELECT * FROM user_log WHERE user_id = '{}';".format(user_id))
        return x

async def get_all_member_profiles():
    x = db.fetch("SELECT * FROM user_log WHERE rank != 'alien';")
    return x

async def get_stickers(user_id):
    if await does_user_exist(user_id):
        x = db.fetch("SELECT * FROM stickers WHERE user_id = '{}';".format(user_id))
        return x

#--- C H A N G E / S E T ---#
async def set_nickname(user_id, new_nickname):
    if await does_user_exist(user_id):
        db.update("UPDATE user_log SET nickname = '{}' WHERE user_id = '{}';".format(new_nickname, user_id))

async def set_rank(user_id, new_rank):
    if await does_user_exist(user_id):
        db.update("UPDATE user_log SET rank = '{}' WHERE user_id = '{}';".format(new_rank, user_id))
        if new_rank == 'alien':
            await set_balance(user_id, 0)
            await set_sticker_allowance(user_id, 0)

async def set_balance(user_id, new_balance):
    if await does_user_exist(user_id):
        db.update("UPDATE user_log SET balance = {} WHERE user_id = '{}';".format(new_balance, user_id))

async def set_sticker_allowance(user_id, new_quantity):
    if await does_user_exist(user_id):
        db.update("UPDATE user_log SET sticker_allowance = {} WHERE user_id = '{}';".format(new_quantity, user_id))

async def ch_balance(user_id, delta):
    if await does_user_exist(user_id):
        current_balance = get_balance(user_id)
        new_balance = current_balance + delta
        db.update("UPDATE user_log SET balance = {} WHERE user_id = '{}';".format(new_balance, user_id))

async def reset_sticker_allowance():
    db.update("UPDATE user_log SET sticker_allowance = 1 WHERE rank = 'owner';")
    db.update("UPDATE user_log SET sticker_allowance = 1 WHERE rank = 'admin';")
    db.update("UPDATE user_log SET sticker_allowance = 1 WHERE rank = 'member';")
    db.update("UPDATE user_log SET sticker_allowance = 0 WHERE rank = 'alien';")

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
    '''mk user <id> <nickname>'''
    text = message.content.split()
    if text[0] == 'mk' and text[1] == 'user' and len(text) == 4:
            user_id = text[2]
            nickname = text[3]
            if await main.verid(user_id):
                await create_new_user(user_id, nickname)

async def create_new_user(user_id, nickname):
    if not await does_user_exist(user_id):
        db.update("INSERT INTO user_log (user_id, nickname) VALUES('{}', '{}');".format(user_id, nickname))
        db.update("INSERT INTO stickers (user_id) VALUES ('{}');".format(user_id))

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
    '''ch bal <id> <+/-><delta>'''
    text = message.content.split()
    if text[0] == 'ch' and text[1] == 'bal' and len(text) == 4:
        delta = text[3]
        user_id = text[2]
        if does_user_exist(user_id) and await str_is_signum_int(delta):
            delta = await signumintstr_to_int(delta)
            await change_balance(user_id, delta)

async def manual_set_balance(message):
    '''set bal <id> <+/-><amount>'''
    text = message.content.split()
    if text[0] == 'set' and text[1] =='bal' and len(text) == 4:
        balance = text[3]
        user_id = text[2]
        if does_user_exist(user_id) and await str_is_signum_int(balance):
            balance = await signumintstr_to_int(balance)
            await set_balance(user_id, balance)
#--- R E S E T ---#
async def manual_reset_stickers(message):
    '''sticker reset'''
    if message.content == 'sticker reset':
        await reset_sticker_allowance()

#--- R E Q U E S T   I N F O ---#
async def request_my_profile(bot, message):
    '''show me'''
    user_id = message.author.id
    x = await get_user_profile(user_id)
    y = await get_stickers(user_id)
    nickname = x[0][1]
    rank = x[0][2]
    balance = x[0][3]
    sticker_allowance = x[0][4]
    stickers = 'pais x{} shib x{} otte x{} page x{} pmogs x{} seal x{} boko x{} kkid x{}, morp x{}, spar x{}'.format(y[0][1], y[0][2], y[0][3], y[0][4], y[0][5], y[0][6], y[0][7], y[0][8], y[0][9], y[0][10]) 
    await bot.send_message(message.author, '**{}**\nrank: {}, balance: {}, sticker allowance: {}\nstickers: {}'.format(nickname, rank, balance, sticker_allowance, stickers))

async def request_specific_profile(bot, message):
    text = message.split()
    user_id = text[1]
    x = await compile_single_profile(user_id)
    await bot.send_message(message.author, x)

async def request_all_profiles(bot, message):
    '''show all'''
    text = message.split()
    sl = await get_all_profiles()
    all_users = []
    for i in range(len(sl)):
        all_users.append(sl[i][0])
    report = ''
    for user_id in all_users:
        current_profile = await compile_single_profile(user_id)
        report += current_profile
    await bot.send_message(message.author, report)
        
async def compile_single_profile(user_id):
    x = await get_user_profile(user_id)
    y = await get_stickers(user_id)
    nickname = x[0][1]
    balance = x[0][2]
    stickers = 'pais x{} shib x{} otte x{} page x{} pmogs x{} seal x{} boko x{} kkid x{}, morp x{}, spar x{}'.forma
t(y[0][1], y[0][2], y[0][3], y[0][4], y[0][5], y[0][6], y[0][7], y[0][8], y[0][9], y[0][10])
    report = '**{}**\nbalance: {}\nstickers: {}\n\n'.format(nickname, balance, stickers)
    return report



