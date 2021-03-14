import pandas as pd
import pathlib
from sys import platform


def data_path():
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
