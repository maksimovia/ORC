import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()


cursor.execute('''CREATE TABLE streams(NAME TEXT, T REAL, P REAL, H REAL, S REAL, Q REAL, G REAL)''')
cursor.execute('''CREATE TABLE blocks(NAME TEXT, Q REAL, N REAL, KPD REAL)''')

cursor.close()
