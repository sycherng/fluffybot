import asyncio, asyncpg, datetime #---outside modules
import secrets #---modules that don't interact with user

async def fetch(*query):
    '''
    (str) -> list of Record objects
    Given a postgres query, returns a list of 1 or more asyncpg Record objects.
    '''
    conn = await asyncpg.connect(user=secrets.db_user, password=secrets.db_password, database=secrets.db_database)
    records_list = await conn.fetch(*query)
    await conn.close()
    return records_list

async def execute(*query):
    '''
    (str) -> bool
    Given a postgres query, attempts to execute the query in the database.
    Returns whether the attempt was successful.
    '''
    conn = await asyncpg.connect(user=secrets.db_user, password=secrets.db_password, database=secrets.db_database)
    try: 
        await conn.execute(*query)
        await conn.close()
    except: return False
    else: 
        return True

async def get_attribute(key_id, attribute, table_name):
    '''
    (str, str, str) -> list of Record objects
    Given the primary key, desired column, and name of a table, returns the value in that cell.
    '''
    records_list = await fetch(f"SELECT {attribute} FROM {table_name} WHERE id = $1", key_id)
    return records_list[0][attribute]


async def get_rank(user_id):
    '''
    (str) -> str
    Given a user's discord id, returns their rank with the bot.
    '''
    return await get_attribute(user_id, 'rank', 'user_objects')

async def user_has_permission(user_id, command_opener):
    '''
    (str, str) -> bool
    Given a user's discord id and the opener for a bot-related command, returns whether the user's rank
    with the bot permits the use of that command. The command opener is as specified in the bot's
    rank_privileges table.
    '''
    rank = await get_rank(user_id)
    records_list = await fetch(f'SELECT {rank} FROM rank_privileges WHERE function = $1', command_opener)
    return records_list[0][rank]

async def is_int(ss):
    '''
    (str) -> bool
    Given a string, returns True if all characters in a string are integers, False otherwise.
    '''
    try: int(ss)
    except: return False
    else: return True

async def is_valid_id(some_id):
    '''
    (str) -> bool
    Given a string representing a user's discord id, returns True if it has the characteristic format
    of valid discord id, False otherwise.
    '''
    return type(some_id) == type('') and 15 <= len(some_id) <= 20 and await is_int(some_id)

async def user_exists(user_id):
    '''
    (str) -> bool
    Given a user's discord id, return True if user exists in bot's database, False otherwise.
    '''
    try: records_list = await get_attribute(user_id, 'id', 'user_objects')
    except: return False
    else:
        return True
