import pandas as pd
import numpy as np
from sys import platform
import base64
import io
import scripts.main.config as config
import scripts.main.models as models
import scripts.main.importer.pl as pl_importer
from scripts.main.base_logger import log


class Mankkoo(models.Importer):

    def load_file_by_filename(self, file_name: str):
        return pd.read_csv(config.data_path() + file_name)

    def load_file_by_contents(self, contents: str):
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        return pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    def format_file(self, df: pd.DataFrame, account_name=None):
        return df

def load_data_from_file(file_type: models.FileType, kind=None, file_name=None, account_name=None):
    result = None
    log.info('Loading %s file', file_type)

    if file_type is models.FileType.ACCOUNT:
        result = pd.read_csv(config.mankkoo_file_path('account'), parse_dates=['Date'])
        result = result.astype({'Account': 'string', 'Balance': 'float', 'Operation': 'float', 'Date': 'datetime64[ns]'})
        result['Date'] = result['Date'].dt.date
        return result

    if file_type is models.FileType.INVESTMENT:
        result = pd.read_csv(config.mankkoo_file_path('investment'), parse_dates=['Start Date', 'End Date'])
        result = result.astype({'Active': 'int', 'Start Amount': 'float', 'End amount': 'float', 'Start Date': 'datetime64[ns]', 'End Date': 'datetime64[ns]'})
        result.Active = result.Active.astype('bool')
        result['Start Date'] = result['Start Date'].dt.date
        result['End Date'] = result['End Date'].dt.date
        return result

    if file_type is models.FileType.STOCK:
        result = pd.read_csv(config.mankkoo_file_path('stock'), parse_dates=['Date'])
        result = result.astype({'Total Value': 'float', 'Date': 'datetime64[ns]'})
        result['Date'] = result['Date'].dt.date
        return result

    if file_type is models.FileType.TOTAL:
        result = pd.read_csv(config.mankkoo_file_path('total'), parse_dates=['Date'])
        result = result.astype({'Date': 'datetime64[ns]', 'Total': 'float'})
        result['Date'] = result['Date'].dt.date
        return result

    if file_type is models.FileType.BANK:
        if file_name is None:
            raise ValueError('Could not load data file. file_name was not provided. In order to load data you need to provide a file name located in data directory.')

        # result = pd.read_csv(config.data_path() + file_name)
        return load_bank_data(file_name, None, kind, account_name)

    raise ValueError('A file_type: {} is not supported'.format(file_type))

def load_bank_data(file_name: str, contents, kind: models.Bank, account_name: str):
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
    if file_name is None and contents is None:
        raise ValueError('Could not load data file. Either "file_name" or "contents" needs to be provided')

    if file_name is not None and contents is not None:
        raise ValueError('Could not load data file. Both "file_name" and "contents" has been provided. Only one of them can be')

    if kind is None:
        raise ValueError('Could not load data file. "kind" (bank, investment, stock) argument was not provided')

    if kind is models.Bank.MANKKOO:
        bank = Mankkoo()
    elif kind is models.Bank.PL_MILLENIUM:
        bank = pl_importer.Millenium()
    elif kind is models.Bank.PL_ING:
        bank = pl_importer.Ing()
    else:
        raise KeyError("Failed to load data from file. Not known bank. Was provided {} bank".format(str(kind)))

    if file_name is not None:
        df = bank.load_file_by_filename(file_name)
    else:
        df = bank.load_file_by_contents(contents)
    return bank.format_file(df, account_name)
