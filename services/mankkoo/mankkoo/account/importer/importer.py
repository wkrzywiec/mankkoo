import pandas as pd
import mankkoo.account.models as models
import mankkoo.account.importer.pl_millenium as pl_millenium_importer
import mankkoo.account.importer.pl_ing as pl_ing_importer
import mankkoo.account.importer.pl_mbank as pl_mbank_importer


def load_bank_data(file_path: str, contents, kind: models.Bank, account_id: str)-> pd.DataFrame:
    """Load data from a CSV file

    Args:
        file_path (str): absolut file location
        contents (bytes): content of a file
        kind (mankkoo.account.models.Bank): bank name
        account_id: id of an account

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
        bank = pl_ing_importer.Ing()
    elif kind is models.Bank.PL_MBANK:
        bank = pl_mbank_importer.Mbank()
    elif kind is models.Bank.PL_MILLENIUM:
        bank = pl_millenium_importer.Millenium()
    else:
        raise KeyError("Failed to load data from file. Not known bank. Was provided {} bank".format(str(kind)))

    if file_path is not None:
        df = bank.load_file_by_filename(file_path)
    else:
        df = bank.load_file_by_contents(contents)
    return bank.format_file(df, account_id)
