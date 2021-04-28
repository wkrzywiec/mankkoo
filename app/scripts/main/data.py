import scripts.main.importer as importer
import scripts.main.config as config
import pandas as pd
import numpy as np
import os

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

def total_money_data(data: dict):

    checking_account = __latest_account_balance(data, '360')
    savings_account = __latest_account_balance(data, 'Konto Oszczędnościowe Profit')
    cash = __latest_account_balance(data, 'Gotówka')
    ppk = __latest_account_balance(data, 'PKO PPK')

    inv = data['investment'].loc[data['investment']['Active'] == True]
    inv = inv['Start Amount'].sum()

    stock_buy = data['stock'].loc[data['stock']['Operation'] == 'Buy']
    stock_buy = stock_buy['Total Value'].sum()
    # TODO check how much stock units I have Broker-Title pair buy-sell
    total = checking_account + savings_account + cash + ppk + inv + stock_buy

    return pd.DataFrame([
        {'Type': 'Checking Account', 'Total': checking_account, 'Percentage': checking_account/total},
        {'Type': 'Savings Account', 'Total': savings_account, 'Percentage': savings_account/total},
        {'Type': 'Cash', 'Total': cash, 'Percentage': cash/total},
        {'Type': 'PPK', 'Total': ppk, 'Percentage': ppk/total},
        {'Type': 'Investments', 'Total': inv, 'Percentage': inv/total},
        {'Type': 'Stocks', 'Total': stock_buy, 'Percentage': stock_buy/total}
    ])

def __latest_account_balance(data: dict, type: str) -> float:
    
    #TODO filter by account type, not name, and if more than one sum it
    df = data['account'].loc[data['account']['Account'] == type]
    if not df.empty:
        return df['Balance'].iloc[-1]
    return 0.00

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