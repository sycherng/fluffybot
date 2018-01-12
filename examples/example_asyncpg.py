import asyncio, asyncpg
import cp_secrets as secrets

'''
Memo: $n can only work as data values, not as identifiers.
'''


async def bar():
    conn = await asyncpg.connect(user=secrets.db_user, password=secrets.db_password, database=secrets.db_database)
    event_id = '00001'
    user_id = '***REMOVED***'
    res = await conn.fetch("select * from event where event_id = $1", event_id)
    if res:
        for record in res:
            for k, v in record.items():
                if v == user_id:
                    print(record)
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
