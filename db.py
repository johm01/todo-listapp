import sqlite3 

db = sqlite3.connect('todo.db')
cur = db.cursor()
#cur.execute('DELETE FROM users')
#db.commit()
cur.execute('SELECT username FROM users')
name = cur.fetchall()
print(name)
#key = 'john'
#for n in name:
    #if n[0] == key:
        #print(key)
    #else:
        #print('no_match')
