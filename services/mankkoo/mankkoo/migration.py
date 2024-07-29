import pandas as pd

import mankkoo.util.config as config
from mankkoo.account import account_db
import mankkoo.event_store as es

# load account.csv
# Row,Account,Date,Title,Details,Category,Comment,Operation,Currency,Balance,Comments

# id,stream_id,type,data,version,occured_at,added_at
streams = es.get_all_streams()

df = account_db.load_all_operations_as_df()

# for each elements in df
    # generate type
    # generate data -> title, details, amount, balance, currency
    # version - append
    # occured_at, added_at

# update streams with version
