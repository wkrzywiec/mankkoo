import pandas as pd
from sys import platform
import accounting.account.models as models
import accounting.account.importer.pl as pl_importer
from accounting.base_logger import log


def load_bank_data(file_path: str, contents, kind: models.Bank, account_id: str)-> pd.DataFrame:
    """Load data from a CSV file

    Args:
        file_type (importer.FileType)*: define which kind of a file needs to be loaded. Currently supported:
            - ACCOUNT - account.csv (from .mankkkoo dir) with operations history from multiple bank accounts
            - INVESTMENT - investment.csv (from .mankkoo dir) with investments history
            - STOCK - stock.csv (from .mankkoo dir) with history of bought and sold shares
            - TOTAL - total.csv (from .mankkoo dir) with total money history
            - BANK - loads an exported file from a bank with transaction history. It requires to provide two addition params kind and file_path
        kind (importer.Bank): used only to load a data from bank exported file
        file_path (str): absolut file location

    Returns:
        [pd.Dataframe]: holds history of operations for an account
    """
    if account_id is None:
        raise ValueError('Could not load data file. "account_id" needs to provided')

    if file_path is None and contents is None:
        raise ValueError('Could not load data file. Either "file_path" or "contents" needs to be provided')

    if file_path is not None and contents is not None:
        raise ValueError('Could not load data file. Both "file_path" and "contents" has been provided. Only one of them can be')

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

    if file_path is not None:
        df = bank.load_file_by_filename(file_path)
    else:
        df = bank.load_file_by_contents(contents)
    return bank.format_file(df, account_id)
