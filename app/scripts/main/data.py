import pandas as pd
import numpy as np
import os
import scripts.main.importer.importer as importer
import scripts.main.models as models
import scripts.main.config as config
import scripts.main.total as total
from scripts.main.base_logger import log

log.basicConfig(level=log.DEBUG)

account_columns = ['Bank', 'Type', 'Account', 'Date', 'Title', 'Details', 'Category', 'Comment', 'Operation', 'Currency', 'Balance']
invest_columns = ['Active', 'Category', 'Bank', 'Investment', 'Start Date', 'End Date', 'Start Amount', 'End amount', 'Currency', 'Details', 'Comment']
stock_columns = ['Broker', 'Date', 'Title', 'Operation', 'Total Value', 'Units', 'Currency', 'Details', 'Url', 'Comment']
total_columns = ['Date', 'Total']


def load_data():
    """Load account.csv file into a Pandas DataFrame

    Returns:
        pandas.DataFrame: DataFrame that holds all historical data
    """
    log.info("Loading mankkoo's files")
    return dict(
        account=importer.load_data(models.FileType.ACCOUNT),
        investment=importer.load_data(models.FileType.INVESTMENT),
        stock=importer.load_data(models.FileType.STOCK),
        total=importer.load_data(models.FileType.TOTAL)
    )

def add_new_operations(bank: models.Bank, file_name: str, account_name: str):
    """Append bank accounts history with new operations. 
    This method return a pandas DataFrame with calculated balance.

    Args:
        bank (importer.Bank): enum of a bank company
        file_name (str): name of a file from which data will be loaded

    Raises:
        KeyError: raised when unsupported bank enum is provided

    Returns:
        pandas.DataFrame: DataFrame that holds transactions history with newly added operations
    """
    log.info('Adding new operations for %s account from a file %s', account_name, file_name)
    df_new = importer.load_data(file_type=models.FileType.BANK, kind=bank, file_name=file_name, account_name=account_name)
    df = importer.load_data(models.FileType.ACCOUNT)
    df = pd.concat([df, df_new]).reset_index(drop=True)

    df = calculate_balance(df, account_name)
    total.update_total_money(df, df_new['Date'])
    df.to_csv(config.mankoo_file_path('account'), index=False)
    log.info('%d new operations for %s account were added.', df_new['Bank'].size, account_name)
    return df

def calculate_balance(df: pd.DataFrame, account_name: str):
    """Calculates balance for new operations

    Args:
        df (pandas.DataFrame): DataFrame with a column 'Balance' which has some rows with value NaN

    Returns:
        pandas.DataFrame: DataFrame with calucated 'Balance' after each operation
    """
    log.info('Calculating balance for %s account.', account_name)
    # TODO move to importer.py
    df = df.astype({'Balance': 'float', 'Operation': 'float'})
    non_balanced_rows = df['Balance'].index[df['Balance'].apply(pd.isna)]

    latest_balance = __latest_balance_for_account(df, account_name)

    log.info('Calculating balance for %s account from %s', account_name, df.iloc[non_balanced_rows[0]]['Date'])
    for i in range(non_balanced_rows[0], len(df)):
        latest_balance = latest_balance + df.loc[i, 'Operation']
        df.loc[i, 'Balance'] = round(latest_balance, 2)

    return df

def __latest_balance_for_account(df: pd.DataFrame, account_name: str):

    result = df.loc[(df['Account'] == account_name)]
    result = result.dropna(subset=['Balance'])
    return result.iloc[-1]['Balance']
