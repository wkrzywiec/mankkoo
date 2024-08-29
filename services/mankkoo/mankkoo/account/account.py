import numpy as np
import pandas as pd
import uuid

import mankkoo.account.importer.importer as importer
import mankkoo.account.account_db as db
import mankkoo.event_store as es
from mankkoo.base_logger import log

log.basicConfig(level=log.DEBUG)


def add_new_operations(
        account_id: str,
        file_name=None,
        contents=None) -> None:
    """Append bank accounts history with new operations.
    This method return a pandas DataFrame with calculated balance.

    Args:
        bank (importer.Bank): enum of a bank company
        file_name (str): name of a file from which data will be loaded
        contents (bytes): content of a file

    Raises:
        KeyError: raised when unsupported bank enum is provided
    """
    log.info('Adding new operations for %s account', account_id)
    bank = db.get_bank_type(account_id)
    df_new = importer.load_bank_data(file_name, contents, bank, account_id)

    log.info(f"{df_new['Account'].size} new operations for {account_id} account were added.")

    events = __prepare_events(account_id, df_new)

    log.info(f"{len(events)} events prepared. Storing them...")
    es.store(events)
    log.info("All events were stored")


def __prepare_events(account_id: str, df: pd.DataFrame) -> list[es.Event]:

    version = 0
    stream_id = uuid.uuid4()

    stream = es.get_stream_by_id(account_id)
    if stream is not None:
        version = stream.version
        stream_id = stream.id
    else:
        log.info(f'No stream found for accountNumber={account_id}. Creating a new one with id={stream_id}')

    events = []
    latest_balance = db.get_account_balance(account_id)

    for _, row in df.iterrows():

        version += 1
        latest_balance = round(latest_balance + row['Operation'], 2)

        event = es.Event(
            stream_type="account",
            stream_id=stream_id,
            event_type="MoneyDeposited" if row['Operation'] > 0 else "MoneyWithdrawn",
            data={"title": __titleOrDefault(row['Title']), "amount": row['Operation'], "currency": row['Currency'], "balance": latest_balance},
            occured_at=row['Date'],
            version=version
        )
        events.append(event)

    return events


def __titleOrDefault(transaction_title) -> str:
    if transaction_title is np.NaN:
        return 'Title not provided'
    else:
        return transaction_title
