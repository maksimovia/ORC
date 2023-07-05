from sqlite import open_db, close_db, read_stream, write_stream

open_db()


write_stream('COND-OUT',2,1,1,1,1,1)
print(read_stream('COND-OUT')['T'])

close_db()
