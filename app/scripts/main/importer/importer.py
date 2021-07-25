import pandas as pd
import numpy as np
from sys import platform
import scripts.main.config as config
import scripts.main.models as models
import scripts.main.importer.pl as pl_importer
from scripts.main.base_logger import log

class Mankkoo(models.Importer):

    def load_file(self, file_name: str, account_name=None):
        return pd.read_csv(config.data_path() + file_name)

def load_data(file_type: models.FileType, kind=None, file_name=None, account_name=None):
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
    log.info('Loading %s file', file_type)
    if file_type is models.FileType.ACCOUNT:
        result = pd.read_csv(config.mankoo_file_path('account'), parse_dates=['Date'])
        result = result.astype({'Account': 'string', 'Balance': 'float', 'Operation': 'float', 'Date': 'datetime64[ns]'})
        result['Date'] = result['Date'].dt.date
        return result

    if file_type is models.FileType.INVESTMENT:
        result = pd.read_csv(config.mankoo_file_path('investment'), parse_dates=['Start Date', 'End Date'])
        result = result.astype({'Active': 'int', 'Start Amount': 'float', 'End amount': 'float', 'Start Date': 'datetime64[ns]', 'End Date': 'datetime64[ns]'})
        result.Active = result.Active.astype('bool')
        result['Start Date'] = result['Start Date'].dt.date
        result['End Date'] = result['End Date'].dt.date
        return result

    if file_type is models.FileType.STOCK:
        result = pd.read_csv(config.mankoo_file_path('stock'), parse_dates=['Date'])
        result = result.astype({'Total Value': 'float', 'Date': 'datetime64[ns]'})
        result['Date'] = result['Date'].dt.date
        return result

    if file_type is models.FileType.TOTAL:
        result = pd.read_csv(config.mankoo_file_path('total'), parse_dates=['Date'])
        result = result.astype({'Date': 'datetime64[ns]', 'Total': 'float'})
        result['Date'] = result['Date'].dt.date
        return result

    if kind is None:
        raise ValueError('Could not load data file. "kind" (bank, investment, stock) argument was not provided')
    if file_name is None:
        raise ValueError('Could not load data file. file_name was not provided. In order to load data you need to provide a file name located in data directory.')

    if file_type is models.FileType.BANK:
        if kind is models.Bank.MANKKOO:
            bank = Mankkoo()
        elif kind is models.Bank.PL_MILLENIUM:
            bank = pl_importer.Millenium()
        else:
            raise KeyError("Failed to load data from file. Not known bank. Was provided {} bank".format(str(kind)))

        return bank.load_file(file_name, account_name)

    raise ValueError('A file_type: {} is not supported'.format(file_type))
