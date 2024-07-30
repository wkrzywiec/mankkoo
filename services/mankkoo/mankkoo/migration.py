from datetime import datetime
import pandas as pd

import mankkoo.util.config as config
from mankkoo.account import account_db
import mankkoo.event_store as es

streams = es.get_all_streams()
streams_version = {key: 0 for key in streams.keys()}

df = account_db.load_all_operations_as_df()

events = []

print(f"Preparing events {df.size}...")

for index, row in df.iterrows():

    version = streams_version[row['Account']]
    version += 1
    
    event = es.Event(
        stream_type="account",
        stream_id=streams[row['Account']],
        event_type="MoneyDeposited" if row['Operation'] > 0 else "MoneyWithdrawn",
        data={ "title": row['Title'], "amount": row['Operation'], "currency": row['Currency'], "balance": row['Balance'], "details": row['Details'], "comment": row['Comment']},
        occured_at= datetime.strptime(row['Date'], "%Y-%m-%d"),
        version=1
    )

    events.append(event)
    streams_version[row['Account']] = version

print(f"{df.size} events prepared. Storing them...")

es.store(events)

