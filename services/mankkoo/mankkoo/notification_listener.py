import asyncio
import psycopg2

import mankkoo.database as db


def handle_notify():
    conn.poll()
    for notify in conn.notifies:
        print('notification received')
        print(notify.payload)
    conn.notifies.clear()


conn = db.get_connection()
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

cursor = conn.cursor()
cursor.execute("LISTEN events_added;")

loop = asyncio.get_event_loop()
loop.add_reader(conn, handle_notify)
loop.run_forever()
