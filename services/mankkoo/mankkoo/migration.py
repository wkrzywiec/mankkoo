# This is a script used only once for migrating data from account.csv file
# to PostgreSQL database.

from datetime import datetime

from account import account_db
import event_store as es
import numpy as np


def emptyOrDefault(argument):
    if argument is np.nan:
        return ''
    else:
        return " ".join(argument.split())


def plnOrDefault(argument):
    if argument is np.nan:
        return 'PLN'
    else:
        return argument


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
        data={"title": emptyOrDefault(row['Title']), "amount": row['Operation'], "currency": plnOrDefault(row['Currency']), "balance": row['Balance']},
        occured_at=datetime.combine(row['Date'], datetime.min.time()),
        version=version
    )

    events.append(event)
    streams_version[row['Account']] = version

print(f"{df.size} events prepared. Storing them...")

es.store(events)

print("All events were stored")
