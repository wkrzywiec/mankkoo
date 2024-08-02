import numpy as np
import pandas as pd
import uuid

import mankkoo.account.importer.importer as importer
import mankkoo.account.account_db as db
import mankkoo.account.models as models
import mankkoo.event_store as es
import mankkoo.total as total
import mankkoo.util.config as config
from mankkoo.base_logger import log

log.basicConfig(level=log.DEBUG)


def add_new_operations(
        account_id: str,
        file_name=None,
        contents=None) -> pd.DataFrame:
    """Append bank accounts history with new operations.
    This method return a pandas DataFrame with calculated balance.

    Args:
        bank (importer.Bank): enum of a bank company
        file_name (str): name of a file from which data will be loaded
        contents (bytes): content of a file

    Raises:
        KeyError: raised when unsupported bank enum is provided

    Returns:
        pandas.DataFrame: DataFrame that holds transactions history
        with newly added operations
    """
    log.info('Adding new operations for %s account', account_id)
    bank = __get_bank_type(account_id)
    df_new = importer.load_bank_data(file_name, contents, bank, account_id)
    df = db.load_all_operations_as_df()
    __make_account_backup(df)

    df = pd.concat([df, df_new]).reset_index(drop=True)
    df = df.sort_values(by=['Date', 'Account'])
    df = df.reset_index(drop=True)
    latest_balance = __latest_balance_for_account(df, account_id)
    df = calculate_balance(df, account_id)
    df.to_csv(config.mankkoo_file_path('account'),
              index=True,
              index_label='Row')

    total.update_total_money(df, df_new['Date'].min())
    total.update_monthly_profit(from_date=df_new['Date'].min(), force=True)
    log.info(
        '%d new operations for %s account were added.',
        df_new['Account'].size,
        account_id)

    __prepare_and_store_events(account_id, df_new, latest_balance)
    return df


def calculate_balance(df: pd.DataFrame, account_id: str) -> pd.DataFrame:
    """Calculates balance for new operations

    Args:
        df (pandas.DataFrame): DataFrame with a column 'Balance' which has some rows with value NaN

    Returns:
        pandas.DataFrame: DataFrame with calucated 'Balance' after each operation
    """
    log.info('Calculating balance for %s account.', account_id)
    # TODO move to importer.py
    df = df.astype({'Balance': 'float', 'Operation': 'float'})
    non_balanced_rows = df['Balance'].index[df['Balance'].apply(pd.isna)]

    latest_balance = __latest_balance_for_account(df, account_id)

    log.info('Calculating balance for %s account from %s', account_id, df.iloc[non_balanced_rows[0]]['Date'])
    for i in non_balanced_rows.values.tolist():
        latest_balance = latest_balance + df.loc[i, 'Operation']
        df.loc[i, 'Balance'] = round(latest_balance, 2)

    return df


def __get_bank_type(account_id: str):
    account_defs = config.load_user_config()['accounts']['definitions']
    account_list = [acc for acc in account_defs if acc['id'] == account_id]

    if len(account_list) == 0:
        raise ValueError(f"Failed to load bank definition. There is no bank account definition with an id '{account_id}'")

    importer = account_list[0]['importer']

    try:
        bank = models.Bank[importer]
        log.info(f"Found bank by account_id ({account_id}): {bank}")
        return bank
    except Exception:
        raise ValueError(f"Failed to load importer for bank. Importer with a code: '{importer}' is not known")


def __latest_balance_for_account(df: pd.DataFrame, account_id: str):

    result = df.loc[(df['Account'] == account_id)]
    result = result.dropna(subset=['Balance'])
    try:
        return result.iloc[-1]['Balance']
    except IndexError:
        log.info(f'There are no latest balance for {account_id} account. Therefore assuming 0.')
        return 0


def __make_account_backup(df: pd.DataFrame):
    df.to_csv(config.mankkoo_file_path('account-backup'), index=True)


def __prepare_and_store_events(account_id: str, df: pd.DataFrame, latest_balance: float):

    version = 1
    stream_id = uuid.uuid4()

    stream = es.get_stream_by_metadata('accountNumber', account_id)
    if stream is not None:
        version = stream.version
        stream_id = stream.id
    else:
        log.info(f'No stream found for accountNumber={account_id}. Creating a new one with id={stream_id}')

    events = []

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

    log.info(f"{len(events)} events prepared. Storing them...")

    es.store(events)

    log.info("All events were stored")


def __titleOrDefault(transaction_title) -> str:
    if transaction_title is np.NaN:
        return 'Title not provided'
    else:
        return transaction_title
