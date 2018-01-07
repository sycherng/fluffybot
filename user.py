import asyncio
import async_db as db, secrets
import main

async def respond(bot, message):
    pass

async def prefix_respond(bot, message):
    await user_add(bot, message)
    await user_set_rank(bot, message)
    await user_set_nickname(bot, message)
    await user_set_balance(bot, message)
    #await user_list(bot, message)

async def spawn_user(message):
    '''|bot|
    (Message object) -> None

    Creates an entry for the message author in the bot's database if one does not exist.
    '''
    if not await db.user_exists(message.author.id):
        await db.execute(f"INSERT INTO user_objects (id, nickname) VALUES $1, $2)", message.author.id, message.author.name)

async def user_add(bot, message):
    '''|user|
    (Bot object, Message object) -> None

    Command: <prefix>user add <target_id> <target_nickname>

    Creates an entry for the target user in the bot's database if one does not exist, and the message
    author has sufficient rank with the bot.
    '''
    command_opener = 'user add'
    if message.content.startswith(command_opener) and await db.user_has_permission(message.author.id, command_opener):
        msg = message.content.split()[2:]
        target_id = msg[0]
        target_nickname = msg[1]

        if await db.user_exists(target_id):
            await bot.send_message(message.author, 'Error: user already exists.')
            
        elif len(msg) == 2 and await db.is_valid_id(target_id):
            try: await db.execute(f"INSERT INTO user_objects (id, nickname, rank) VALUES ($1, $2, 'member')", target_id, target_nickname)
            except Exception as error:
               await notify_owner(bot, command_opener, message.author, error)
            else:
               await bot.send_message(message.author, 'Ok, user created.')


async def user_set_rank(bot, message):
    '''|user|
    (Bot object, Message object) -> None
    
    Command: <prefix>user set rank <target_id><target_rank>

    Changes target user's rank with bot if user already exists in bot's database, and the message author
    has sufficient rank with the bot.
    '''
    command_opener = 'user set rank'
    if message.content.startswith(command_opener) and await db.user_has_permission(message.author.id, command_opener):
        msg = message.content.split()[3:]
        target_id = msg[0]
        goal_rank = msg[1]

        if len(msg) == 2 and await db.user_exists(target_id) and goal_rank in ['member', 'friend', 'alien']:
            target_curr_rank = await db.get_attribute(target_id, 'rank', 'user_objects')
            if goal_rank != target_curr_rank:
                try: await db.execute(f"UPDATE user_objects SET rank = $1 WHERE id = $2;", goal_rank, target_id)
                except Exception as error: await notify_owner(bot, command_opener, message.author, error)
                else: await bot.send_message(message.author, 'Success: rank changed.')

async def user_set_nickname(bot, message):
    '''|user|
    (Bot object, Message Object) - > None

    Command: <prefix>user set nickname <target_id><target_nickname>

    Changes target user's nickname with bot if user already exists in bot's database, and the message
    author has sufficient rank with the bot.
    '''
    command_opener = 'user set nickname'
    if message.content.startswith(command_opener) and await db.user_has_permission(message.author.id, command_opener):
        msg = message.content.split()[3:]
        target_id = msg[0]
        target_nickname = msg[1]
        if len(msg) == 2 and await db.user_exists(target_id):
            try: await db.execute(f"UPDATE user_objects SET nickname = $1 WHERE id = $2", target_nickname, target_id)
            except Exception as error: await notify_owner(bot, command_opener, message.author, error)
            else: await bot.send_message(message.author, 'Success: nickname updated.')

async def user_set_balance(bot, message):
    '''|user|

    Command: <prefix>user set balance <target_id><target_balance>

    Changes target user's balance with bot if user already exists in bot's database, and the message
    author has sufficient rank with the bot.
    '''
    command_opener = 'user set balance'
    if message.content.startswith(command_opener) and await db.user_has_permission(message.author.id, command_opener):
        msg = message.content.split()[3:]
        target_id = msg[0]
        try: target_balance = int(msg[1])
        except: await bot.send_message(message.author, "Error: illegal balance.")
        else:
            if len(msg) == 2 and await db.user_exists(target_id) and target_balance >= 0:
                try: await db.execute(f"UPDATE user_objects SET balance = $1 WHERE id = $2", target_balance, target_id)
                except Exception as error: await notify_owner(bot, command_opener, message.author, error)
                else: await bot.send_message(message.author, 'Success: balance updated.')

'''
async def user_list(bot, message):
    Note: The below functions are out of date. Please refactor for asyncpg and test.
    
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
    db.execute(f"UPDATE {db.users} SET balance = balance {sign} {value} WHERE id = %s;", (target, ))
'''

async def notify_owner(bot, command_opener, author, error):
    '''|bot|
    (Bot object, str, User object) -> None

    Given bot, command opener, and author of a failed command attempt, Direct Message the owner
    about the failure.
    '''
    author_nickname = await db.get_attribute(author.id, 'nickname', 'user_objects')
    await bot.send_message(secrets.bot_owner, f'`{command_opener}` command from {author_nickname} failed with error:\n```{error}```')
