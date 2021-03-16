import pandas as pd
import numpy as np
import pathlib
from sys import platform


def data_path() -> str:
    """Get full path of data directory. Currently supporrted only for Linux and Windows

    Raises:
        ValueError: raised for MacOS, as it's not supported

    Returns:
        [str]: full path to data directory
    """
    scripts_path = str(pathlib.Path(__file__).parent.absolute())

    if platform == "linux":
        return scripts_path.rsplit("/", 1)[0] + "/data/"
    elif platform == "win32":
        return scripts_path.rsplit("\\", 1)[0] + "\\data\\"
    elif platform == "darwin":
        raise ValueError("MacOS is currently not supported")

def load_data(file_name: str):
    """Load data from a CSV file

    Args:
        file_location (str): full path 

    Returns:
        [pd.Dataframe]: holds history of operations for an account
    """
    return pd.read_csv(data_path() + file_name)

def load_pl_mbank(file_name: str):
    pass

def load_pl_millenium(file_name: str):
    df = load_data(file_name)
    df = df[['Data transakcji', 'Opis', 'Obciążenia', 'Uznania', 'Waluta']]
    df['Operation'] = np.where(
        df['Obciążenia'] < 0, df['Obciążenia'], df['Uznania'])
    df = df.drop(columns=['Obciążenia', 'Uznania'])
    df = df.rename(columns={'Data transakcji': 'Date', 'Opis': 'Title', 'Waluta': 'Currency'})
    df['Bank'] = 'Millenium'
    return __add_missing_columns(df, ['Category', 'Comment'])


def __add_missing_columns(df: pd.DataFrame, columns):
    existing_columns = list(df.columns)
    return df.reindex(columns= existing_columns + columns)
