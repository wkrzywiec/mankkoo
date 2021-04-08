import scripts.main.importer as importer
import scripts.main.config as config
import pandas as pd
import numpy as np
import os

account_columns = ['Bank', 'Account', 'Date', 'Title', 'Details', 'Category', 'Comment', 'Operation', 'Currency', 'Balance']
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

    print('Account')
    checking_account = data['account'].loc[data['account']['Account'] == '360 Account']
    checking_account = checking_account['Balance'].iloc[-1]

    # print('Oszczedno')
    # savings_account = data['account'].loc[data['account']['Account'] == 'Konto Oszczędnościowe Profit']
    # savings_account = savings_account['Balance'].iloc[-1]

    # print('Gotówka')
    # cash = data['account'].loc[data['account']['Account'] == 'Gotówka']
    # cash = cash['Balance'].iloc[-1]

    # print('PPK')
    # ppk = data['account'].loc[data['account']['Account'] == 'PKO PPK']
    # ppk = ppk['Balance'].iloc[-1]

    inv = data['investment'].loc[data['investment']['Active'] == True]
    print(inv)
    inv = inv['Start Amount'].sum()

    stock_buy = data['stock'].loc[data['stock']['Operation'] == 'Buy']
    stock_buy = stock_buy['Total Value'].sum()
    # TODO check how much stock units I have Broker-Title pair buy-sell

    return [
        {'Type': 'Checking Account', 'Total ammount': checking_account},
        {'Type': 'Savings Account', 'Total ammount': 0.00},
        {'Type': 'Cash', 'Total ammount': 0.00},
        {'Type': 'PPK', 'Total ammount': 0.00},
        {'Type': 'Investments', 'Total ammount': inv},
        {'Type': 'Stocks', 'Total ammount': stock_buy}
    ]

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
    df_new = importer.load_data(importer.FileType.BANK, bank, file_name)
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