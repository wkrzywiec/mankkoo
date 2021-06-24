import pandas as pd
import numpy as np
from sys import platform
import scripts.main.config as config
from enum import Enum

# TODO move all enums to models.py
class FileType(Enum):
    ACCOUNT = 'account'
    INVESTMENT = 'investment'
    STOCK = 'stock'
    TOTAL = 'total'
    BANK = 'bank'

class Bank(Enum):
    """Representations of supported bank reports exports. Special value is MANKKOO, which is used to load a file in mankkoo format

    Args:
        Enum (str): country and name of a bank
    """
    MANKKOO = 'mankkoo'
    PL_MBANK = 'pl_mbank'
    PL_MILLENIUM = 'pl_millenium'
    PL_IDEA = 'pl_idea'

class Account(Enum):
    """Representations of different kinds of account, like checking, savings, cash or for retirement

    Args:
        Enum (str): string name of a type
    """
    CHECKING = 'checking'
    SAVINGS = 'savings'
    RETIREMENT = 'retirement'
    CASH = 'cash'

def load_data(file_type: FileType, kind=None, file_name=None):
    """Load data from a CSV file

    Args:
        file_type (importer.FileType)*: define which kind of a file needs to be loaded. Currently supported:
            - ACCOUNT - account.csv (from .mankkkoo dir) with operations history from multiple bank accounts
            - INVESTMENT - investment.csv (from .mankkoo dir) with investments history
            - STOCK - stock.csv (from .mankkoo dir) with history of bought and sold shares
            - TOTAL - total.csv (from .mankkoo dir) with total money history
            - BANK - loads an exported file from a bank with transaction history. It requires to provide two addition params kind and file_name
        kind (importer.Bank): used only to load a data from bank exported file
        file_name (str): name of a file located in /data directory

    Returns:
        [pd.Dataframe]: holds history of operations for an account
    """
    if file_type is FileType.ACCOUNT:
        return pd.read_csv(config.mankoo_file_path('account'))

    if file_type is FileType.INVESTMENT:
        return pd.read_csv(config.mankoo_file_path('investment'))

    if file_type is FileType.STOCK:
        return pd.read_csv(config.mankoo_file_path('stock'))

    if file_type is FileType.TOTAL:
        return pd.read_csv(config.mankoo_file_path('total'))

    if kind is None:
        raise ValueError('Could not load data file. "kind" (bank, investment, stock) argument was not provided')
    if file_name is None:
        raise ValueError('Could not load data file. file_name was not provided. In order to load data you need to provide a file name located in data directory.')

    if file_type is FileType.BANK:
        if kind is Bank.MANKKOO:
            return __read_from_data_path(file_name)
        elif kind is Bank.PL_MILLENIUM:
            return load_pl_millenium(file_name)
        else:
            raise KeyError("Failed to load data from file. Not known bank. Was provided {} bank".format(str(kind)))

    raise ValueError('A file_type: {} is not supported'.format(file_type))

def load_pl_idea(file_name: str):
    """Load data from CSV file for Idea bank (PL) - https://www.ideabank.pl

    Args:
        file_name (str): name of a file located in /data directory

    Returns:
        [pd.Dataframe]: all operations transformed to common format 
    """
    raise NotImplementedError()

def load_pl_ing(file_name: str):
    """Load data from CSV file for ING bank (PL) - https://www.ing.pl

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
    df = __read_from_data_path(file_name)
    df = df[['Data transakcji', 'Opis', 'Obciążenia', 'Uznania', 'Waluta']]
    
    df['Operation'] = np.where(df['Obciążenia'] < 0, df['Obciążenia'], df['Uznania'])
    df = df.drop(columns=['Obciążenia', 'Uznania'])
    
    df = df.rename(columns={'Data transakcji': 'Date', 'Opis': 'Title', 'Waluta': 'Currency'})
    
    df['Date'] = pd.to_datetime(df.Date)
    df['Bank'] = 'Millenium'
    df['Type'] = Account.CHECKING.value
    df['Account'] = account_name if account_name is not None else 'Millenium Account'
    df['Bank'] = df['Bank'].astype('string')
    return __add_missing_columns(df, ['Category', 'Comment'])

def __read_from_data_path(file_name: str):
    return pd.read_csv(config.data_path() + file_name)

def __add_missing_columns(df: pd.DataFrame, columns):
    existing_columns = list(df.columns)
    return df.reindex(columns= existing_columns + columns)
