import asyncio, asyncpg
import cp_secrets as secrets

'''
Memo: $n can only work as data values, not as identifiers.
'''


async def bar():
    conn = await asyncpg.connect(user=secrets.db_user, password=secrets.db_password, database=secrets.db_database)
    author_id = '2222222222222222'
    author_name = 'Meow-test#9829'
    await conn.execute(f"INSERT INTO user_objects (id, nickname) VALUES ($1, $2)", author_id, author_name[:-5])
    await conn.close()



    '''|Ex 1|
    records_list = await conn.fetch('select * from user_objects where rank = $1', 'owner')
    await conn.close()
    print(records_list) #the list of 1 or more objects
    print(records_list[0]) #the first object
    print(records_list[0]['nickname']) #the nickname of the first object
    '''
    '''|Ex 2|
    records_list2 = await conn.fetch(f"SELECT {'member'} FROM {'rank_privileges'} WHERE function = $1",
    'user list')
    await conn.close()
    print(records_list2)
    print(records_list2[0])
    print(records_list2[0]['member'])
    print(type(records_list2[0]['member']))
    '''




asyncio.get_event_loop().run_until_complete(bar())
