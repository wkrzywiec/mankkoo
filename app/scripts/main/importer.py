import pandas as pd
import numpy as np
from sys import platform
import scripts.main.config as config
from enum import Enum

class Bank(Enum):
    """Representations of supported bank reports exports. Special value is MANKKOO, which is used to load a file in mankkoo format

    Args:
        Enum (str): country and name of a bank
    """
    MANKKOO = 'mankkoo'
    PL_MBANK = 'pl_mbank'
    PL_MILLENIUM = 'pl_millenium'
    PL_IDEA = 'pl_idea'

def load_data(kind: str, file_name=None):
    """Load data from a CSV file

    Args:
        type (str): type of a file that needs to be loaded. If 'account' is provided it will load account.csv file from home directory. If 'bank' is provided than a bank file located in data dir will be loaded
        file_name (str): name of a file located in /data directory

    Returns:
        [pd.Dataframe]: holds history of operations for an account
    """
    if kind == 'account':
        return pd.read_csv(config.mankoo_account_path())

    if kind == 'bank':
        if not file_name:
            raise ValueError('file_name was not provided. In order to load data you need to provide a file name located in data directory.')
        return pd.read_csv(config.data_path() + file_name)

    raise ValueError('A kind of a file to be loaded was not provided.')

def load_pl_idea(file_name: str):
    """Load data from CSV file for Idea bank (PL) - https://www.ideabank.pl

    Args:
        file_name (str): name of a file located in /data directory

    Returns:
        [pd.Dataframe]: all operations transformed to common format 
    """
    raise NotImplementedError()

def load_pl_mbank(file_name: str):
    """Load data from CSV file for Mbank bank (PL) - https://www.mbank.pl

    Args:
        file_name (str): name of a file located in /data directory

    Returns:
        [pd.Dataframe]: all operations transformed to common format 
    """
    raise NotImplementedError()

def load_pl_millenium(file_name: str, account_name=None):
    """Load data from CSV file for Millenium bank (PL) - https://www.bankmillennium.pl

    Args:
        file_name (str): name of a file located in /data directory

    Returns:
        [pd.Dataframe]: all operations transformed to common format 
    """
    df = load_data(kind='bank', file_name=file_name)
    df = df[['Data transakcji', 'Opis', 'Obciążenia', 'Uznania', 'Waluta']]
    
    df['Operation'] = np.where(df['Obciążenia'] < 0, df['Obciążenia'], df['Uznania'])
    df = df.drop(columns=['Obciążenia', 'Uznania'])
    
    df = df.rename(columns={'Data transakcji': 'Date', 'Opis': 'Title', 'Waluta': 'Currency'})
    
    df['Date'] = pd.to_datetime(df.Date)
    df['Bank'] = 'Millenium'
    df['Account'] = account_name if account_name is not None else 'Millenium Account'
    df['Bank'] = df['Bank'].astype('string')
    return __add_missing_columns(df, ['Category', 'Comment'])


def __add_missing_columns(df: pd.DataFrame, columns):
    existing_columns = list(df.columns)
    return df.reindex(columns= existing_columns + columns)
