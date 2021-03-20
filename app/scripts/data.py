from enum import Enum
import app.scripts.importer as importer
import pandas as pd
import numpy as np
import os
from sys import platform

class Bank(Enum):
    PL_MBANK = 'pl_mbank'
    PL_MILLENIUM = 'pl_millenium'
    PL_IDEA = 'pl_idea'

mankkoo_dir = '.mankkoo'
account_file = 'account.csv'

columns = ["Bank", "Date", "Title", "Details", "Category", "Comment", "Operation", "Currency","Balance"]

def init_data_folder():
    home = os.path.expanduser("~")

    if platform == "linux":
        slash = "/"
    elif platform == "win32":
        slash = "\\"
    elif platform == "darwin":
        raise ValueError("MacOS is currently not supported")

    mankkoo_path = home + slash + mankkoo_dir
    if not os.path.exists(mankkoo_path):
        os.makedirs(mankkoo_path)
    df = pd.DataFrame(columns=columns)
    df.to_csv(mankkoo_path + slash + account_file)


def add_new_operations(bank: Bank, file_name: str):
    """Append bank accounts history with new operations. 
    This method return a pandas DataFrame with calculated balance.

    Args:
        bank (Bank): enum of a bank company
        file_name (str): name of a file from which data will be loaded

    Raises:
        KeyError: raised when unsupported bank enum is provided

    Returns:
        pandas.DataFrame: DataFrame that holds transactions history with newly added operations
    """
    
    if bank == Bank.PL_MILLENIUM:
        df_new = importer.load_pl_millenium(file_name)
    else:
        raise KeyError("Failed to load data from file. Not known bank. Was provided {} bank".format(bank))
    
    df = importer.load_data(account_file)
    df = pd.concat([df, df_new]).reset_index(drop=True)

    # TODO save in .mankkoo directory
    df = calculate_balance(df)
    df.to_csv(account_file)
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