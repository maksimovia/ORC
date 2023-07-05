def open_db():
    import sqlite3
    global connection
    global cursor

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='streams' ''')

    if cursor.fetchone() is None:
        cursor.execute('''CREATE TABLE IF NOT EXISTS streams
        (NAME TEXT DEFAULT NULL,
        T REAL DEFAULT NULL,
        P REAL DEFAULT NULL,
        H REAL DEFAULT NULL,
        S REAL DEFAULT NULL,
        Q REAL DEFAULT NULL,
        G REAL DEFAULT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS blocks
        (NAME TEXT DEFAULT NULL,
        Q REAL DEFAULT NULL,
        N REAL DEFAULT NULL,
        KPD REAL DEFAULT NULL)''')

        cursor.execute('''INSERT INTO streams(NAME) VALUES
        ('IN-HEAT'),
        ('HEAT-OUT'),
        ('COND-PUMP'),
        ('PUMP-HEAT'),
        ('HEAT-TURB'),
        ('TURB-COND'),
        ('IN-COND'),
        ('COND-OUT') 
        ''')

        cursor.execute('''INSERT INTO blocks(NAME) VALUES
        ('PUMP'),
        ('TURBINE'),
        ('REGEN'),
        ('CONDENSER'),
        ('HEATER')
        ''')
    pass


def close_db():
    connection.commit()
    cursor.close()
    connection.close()
    pass


def write_stream(stream, t, p, h, s, q, g):
    cursor.execute('''UPDATE streams SET T=?,P=?, H=?, S=?, Q=?, G=? WHERE NAME==? ''', [t, p, h, s, q, g, stream])
    pass


def read_stream(stream):
    t = cursor.execute('''SELECT T FROM streams WHERE NAME==? ''', [stream]).fetchone()
    p = cursor.execute('''SELECT P FROM streams WHERE NAME==? ''', [stream]).fetchone()
    h = cursor.execute('''SELECT H FROM streams WHERE NAME==? ''', [stream]).fetchone()
    s = cursor.execute('''SELECT S FROM streams WHERE NAME==? ''', [stream]).fetchone()
    q = cursor.execute('''SELECT Q FROM streams WHERE NAME==? ''', [stream]).fetchone()
    g = cursor.execute('''SELECT G FROM streams WHERE NAME==? ''', [stream]).fetchone()
    return {'T': t, 'P': p, 'H': h, 'S': s, 'Q': q, 'G': g}
