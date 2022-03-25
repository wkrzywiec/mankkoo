import pandas as pd
from sys import platform
import scripts.main.models as models
import scripts.main.importer.pl as pl_importer
from scripts.main.base_logger import log


def load_bank_data(file_name: str, contents, kind: models.Bank, account_name: str)-> pd.DataFrame:
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

    if kind is models.Bank.PL_ING:
        bank = pl_importer.Ing()
    elif kind is models.Bank.PL_MBANK:
        bank = pl_importer.Mbank()
    elif kind is models.Bank.PL_MILLENIUM:
        bank = pl_importer.Millenium()
    else:
        raise KeyError("Failed to load data from file. Not known bank. Was provided {} bank".format(str(kind)))

    if file_name is not None:
        df = bank.load_file_by_filename(file_name)
    else:
        df = bank.load_file_by_contents(contents)
    return bank.format_file(df, account_name)
