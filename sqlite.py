import sqlite3


def open_db():
    global connection
    global cursor

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    if cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='streams' ''').fetchone() is None:
        cursor.execute('''CREATE TABLE IF NOT EXISTS streams
        (NAME TEXT DEFAULT NULL,
        T REAL DEFAULT NULL,
        P REAL DEFAULT NULL,
        H REAL DEFAULT NULL,
        S REAL DEFAULT NULL,
        Q REAL DEFAULT NULL,
        G REAL DEFAULT NULL,
        X TEXT DEFAULT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS blocks
        (NAME TEXT DEFAULT NULL,
        Q REAL DEFAULT NULL,
        KPD REAL DEFAULT NULL)''')

        cursor.execute('''INSERT INTO streams(NAME) VALUES
        ('IN-HEAT'),
        ('HEAT-OUT'),
        ('COND-PUMP'),
        ('PUMP-HEAT'),
        ('HEAT-TURB'),
        ('TURB-COND'),
        ('IN-COND'),
        ('COND-OUT'),
        ('PUMP-REGEN'),
        ('REGEN-HEAT'),
        ('TURB-REGEN'),
        ('REGEN-COND')
        ''')

        cursor.execute('''INSERT INTO blocks(NAME) VALUES
        ('PUMP'),
        ('TURBINE'),
        ('CONDENSER'),
        ('HEATER'),
        ('REGEN')
        ''')
    print('open DB')
    pass


def close_db():
    connection.commit()
    cursor.close()
    connection.close()
    print('close DB')
    pass


def write_stream(stream, t, p, h, s, q, g, x):
    cursor.execute('''UPDATE streams SET T=?,P=?, H=?, S=?, Q=?, G=?, X=? WHERE NAME==? ''',
                   [t, p, h, s, q, g, x, stream])
    pass


def write_block(block, q):
    cursor.execute('''UPDATE blocks SET Q=? WHERE NAME==? ''', [q, block])
    pass


def read_block(block):
    q = cursor.execute('''SELECT Q FROM blocks WHERE NAME==? ''', [block]).fetchone()
    return {'Q': q[0]}


def read_stream(stream):
    t = cursor.execute('''SELECT T FROM streams WHERE NAME==? ''', [stream]).fetchone()
    p = cursor.execute('''SELECT P FROM streams WHERE NAME==? ''', [stream]).fetchone()
    h = cursor.execute('''SELECT H FROM streams WHERE NAME==? ''', [stream]).fetchone()
    s = cursor.execute('''SELECT S FROM streams WHERE NAME==? ''', [stream]).fetchone()
    q = cursor.execute('''SELECT Q FROM streams WHERE NAME==? ''', [stream]).fetchone()
    g = cursor.execute('''SELECT G FROM streams WHERE NAME==? ''', [stream]).fetchone()
    x = cursor.execute('''SELECT X FROM streams WHERE NAME==? ''', [stream]).fetchone()
    return {'T': t[0], 'P': p[0], 'H': h[0], 'S': s[0], 'Q': q[0], 'G': g[0], 'X': x[0]}
