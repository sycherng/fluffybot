import asyncio
import psycopg2
import secrets

#---database table names
connection = secrets.connection
users = "user_objects"
permissions = "rank_privileges"

def fetch(query, parameters):
    conn = psycopg2.connect(connection)
    cur = conn.cursor()
    cur.execute(query, parameters)    
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def update(query, parameters):
    conn = psycopg2.connect(connection)
    cur = conn.cursor()
    cur.execute(query, parameters)
    conn.commit()
    cur.close()
    conn.close()

def check(userid, attribute, table):
    x = fetch("SELECT {} FROM {} WHERE id  = %s;".format(attribute, table), (userid,))
    if x:
        return x[0][0]
    else:
        return False

def rank_check(userid, function):
    rank = check(userid, 'rank', users)
    query = fetch("SELECT {} FROM {} WHERE FUNCTION = %s;".format(rank, permissions), (function,))
    if not query:
        return False
    if query[0][0] == True:
        return True
    return False

def is_int(ss):
    """ Is the given string an integer? """
    try: int(ss)
    except ValueError: return False
    else: return True

def is_valid_id(ss):
    '''verifies if id is likely a valid discord id'''
    if type(ss) == type('') and len(ss) >= 15 and len(ss) <= 20 and is_int(ss):
        return True
    return False

