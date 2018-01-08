import asyncio, asyncpg
import secrets

#can only work as data values but not identifiers
'''
async def foo():
    conn = await asyncpg.connect(user=secrets.db_user, password=secrets.db_password, database=secrets.db_database)
    records_list = await conn.fetch('select * from user_objects where rank = $1', 'owner')
    print(records_list) #the list of 1 or more objects
    print(records_list[0]) #the first object
    print(records_list[0]['nickname']) #the nickname of the first object
    await conn.close()
'''
async def bar():
    conn = await asyncpg.connect(user=secrets.db_user, password=secrets.db_password, database=secrets.db_database)
    records_list2 = await conn.fetch(f"SELECT {'member'} FROM {'rank_privileges'} WHERE function = $1",
    'user list')
    await conn.close()
    print(records_list2)
    print(records_list2[0])
    print(records_list2[0]['member'])
    print(type(records_list2[0]['member']))

asyncio.get_event_loop().run_until_complete(bar())
