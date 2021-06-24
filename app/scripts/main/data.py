import pandas as pd
import numpy as np
import os
import scripts.main.importer as importer
import scripts.main.config as config
import scripts.main.total as total

account_columns = ['Bank', 'Type', 'Account', 'Date', 'Title', 'Details', 'Category', 'Comment', 'Operation', 'Currency', 'Balance']
invest_columns = ['Active', 'Category', 'Bank', 'Investment', 'Start Date', 'End Date', 'Start Amount', 'End amount', 'Currency', 'Details', 'Comment']
stock_columns = ['Broker', 'Date', 'Title', 'Operation', 'Total Value', 'Units', 'Currency', 'Details', 'Url', 'Comment']

def load_data():
    """Load account.csv file into a Pandas DataFrame

    Returns:
        pandas.DataFrame: DataFrame that holds all historical data
    """
    return dict(
        account = importer.load_data(importer.FileType.ACCOUNT),
        investment = importer.load_data(importer.FileType.INVESTMENT),
        stock = importer.load_data(importer.FileType.STOCK)
    )

def add_new_operations(bank: importer.Bank, file_name: str):
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
    df_new = importer.load_data(file_type=importer.FileType.BANK, kind=bank, file_name=file_name)
    df = importer.load_data(importer.FileType.ACCOUNT)
    df = pd.concat([df, df_new]).reset_index(drop=True)

    df = calculate_balance(df)
    total.update_total_money(df, df_new['Date'])
    df.to_csv(config.mankoo_file_path('account'), index=False)
    return df
    
def calculate_balance(df: pd.DataFrame):
    """Calculates balance for new operations

    Args:
        df (pandas.DataFrame): DataFrame with a column 'Balance' which has some rows with value NaN

    Returns:
        pandas.DataFrame: DataFrame with calucated 'Balance' after each operation
    """
    df = df.astype({'Balance': 'float', 'Operation': 'float'})
    nan_index = df['Balance'].index[df['Balance'].apply(pd.isna)]

    for i in range(nan_index[0], len(df)):
        df.loc[i, 'Balance'] = df.loc[i-1, 'Balance'] + df.loc[i, 'Operation']
    
    return df