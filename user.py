import asyncio
import db
import main

async def respond(bot, message):
    pass

async def prefix_respond(bot, message):
    await user_add(bot, message)
    await user_set_rank(bot, message)
    await user_set_nickname(bot, message)
    await user_set_balance(bot, message)
    await user_list(bot, message)

async def spawn_user(message):
    if not db.check(message.author.id, 'id', db.users):
        db.update("INSERT INTO {} (id, nickname) VALUES (%s, %s);".format(db.users), (message.author.id, message.author.name))

async def user_add(bot, message):
    #--- call: user add <id> <nickname>
    if message.content.startswith('user add '):
        msg = message.content.split()[2:]
        target = msg[0]
        goal_nickname = msg[1]
        if db.rank_check(message.author.id, 'user add') and len(msg) == 2 and db.is_valid_id(target):
            if db.user_exists(target):
                await bot.send_message(message.author, 'Error: user already exists.')
            else:
                db.update("INSERT INTO {} (id, nickname, rank) VALUES (%s, %s, 'member');".format(db.users), (target, goal_nickname))
                await bot.send_message(message.author, 'Ok, user created.')

async def user_set_rank(bot, message):
    #--- call: user set rank <id> <rank>
    if message.content.startswith('user set rank '):
        msg = message.content.split()[3:]
        target = msg[0]
        goal_rank = msg[1]
        if db.rank_check(message.author.id, 'user set rank') and len(msg) == 2 and db.user_exists(target) and goal_rank in ['member', 'friend', 'alien']:
            target_curr_rank = db.check(target, 'rank', db.users)
            if goal_rank != target_curr_rank:
                db.update(f"UPDATE {db.users} SET {'rank'} = %s WHERE id = %s;", (goal_rank, target))
                await bot.send_message(message.author, 'Success: rank changed.')

async def user_set_nickname(bot, message):
    #--- call: user set nickname <id> <nickname>
    if message.content.startswith('user set nickname '):
        msg = message.content.split()[3:]
        target = msg[0]
        goal_nickname = msg[1]
        if db.rank_check(message.author.id, 'user set nickname') and len(msg) == 2 and db.user_exists(target):
            db.update(f"UPDATE {db.users} SET {'nickname'} = %s WHERE id = %s;", (goal_nickname, target))
            await bot.send_message(message.author, 'Success: nickname updated.')

async def user_set_balance(bot, message):
    #--- call: user set balance <id> <amount>
    if message.content.startswith('user set balance '):
        msg = message.content.split()[3:]
        target = msg[0]
        goal_balance = int(msg[1])
        if db.rank_check(message.author.id, 'user set balance') and len(msg) == 2 and db.user_exists(target) and goal_balance >= 0:
            db.update(f"UPDATE {db.users} SET {'balance'} = %s WHERE id = %s;", (goal_balance, target))
            await bot.send_message(message.author, 'Success: balance updated.')

async def user_list(bot, message):
    #---call: user list <id> <id> ...  OR user list *
    #MUST CHECK IF USER EXISTS
    if message.content.startswith('user list '):
        if db.rank_check(message.author.id, 'user list'):
            msg = message.content.split()[2:]
            if msg[0] == '*':
                query = db.fetch(f"select * from {db.users};", ())
            else: #msg is a list of discord ids
                ss = ''
                for element in msg:
                    if db.is_valid_id(element):
                        ss+= f"id = '{element}' or "
                ss += "id = ''"
                query = db.fetch(f"select * from {db.users} where {ss}", ())
            if query:
                pp = ''
                for index in range(len(query)):
                    pp += format_user(query, index)
                await bot.send_message(message.author, pp)
            else:
                await bot.send_message(message.author, "Error: none of supplied ids are in my database. Check if they are valid discord ids, then add them as users.")

def format_user(arr, index):
    res = arr[index]
    id = res[0]
    nickname = res[1]
    rank = res[2]
    balance = res[3]
    return f"{nickname} ({id})\nrank: {rank}, balance: {balance}\n\n"

async def bot_alter_balance(sign, value, target): 
    db.update(f"UPDATE {db.users} SET balance = balance {sign} {value} WHERE id = %s;", (target, ))


