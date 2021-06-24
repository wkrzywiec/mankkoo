import os
import pathlib
from sys import platform
import logging as log
import scripts.main.data as data
import pandas as pd

mankkoo_dir = '.mankkoo'
account_file = 'account.csv'
investment_file = 'investment.csv'
stock_file = 'stock.csv'

def init_data_folder():
    """Initilize .mankkoo directory in home folder and account.csv file inside of it
    """
    mankkoo_path = mankoo_path()
    mankoo_account_file = mankoo_file_path('account')

    log.info('Initializing mankkoo directory and files')

    if not os.path.exists(mankkoo_path):
        log.info('Creating mankkoo directory')
        os.makedirs(mankkoo_path)

    if not os.path.exists(mankoo_account_file):
        log.info("Creating mankkoo's account file")
        df = pd.DataFrame(columns=data.account_columns)
        df.to_csv(mankoo_account_file)
        
    # TODO init pozostałe pliki

def mankoo_file_path(file: str):
    """Get full path of one of mankkoo's files. 

    Args:
        file (str): Which file needs to be loaded. Supported values: 'account', 'investment' and 'stock'

    Raises:
        ValueError: raised when invalid file type has been provided

    Returns:
        str: full path to the mankkoo's data file
    """
    path = mankoo_path() + __slash()

    if file in {'account', 'investment', 'stock'}:
        return path + file + '.csv'

    raise ValueError("Can't get mankkoo file. Unsupported file type: {}".format(file))

def mankoo_path():
    """Get full path to the .mankkoo directory

    Returns:
        str: full path to .mankkoo directory
    """
    return os.path.expanduser("~") + __slash() + mankkoo_dir

def __slash():
    if platform == "linux":
        return "/"
    if platform == "win32":
        return "\\"
    if platform == "darwin":
        raise ValueError("MacOS is currently not supported")
    raise ValueError("{} OS is not supported".format(platform))

def data_path() -> str:
    """Get full path of data directory. Currently supporrted only for Linux and Windows

    Raises:
        ValueError: raised for MacOS, as it's not supported

    Returns:
        [str]: full path to data directory
    """
    scripts_path = str(pathlib.Path(__file__).parent.absolute())

    if platform == "linux":
        return scripts_path.rsplit("/", 2)[0] + "/data/"
    if platform == "win32":
        return scripts_path.rsplit("\\", 2)[0] + "\\data\\"
    if platform == "darwin":
        raise ValueError("MacOS is currently not supported")
    raise ValueError("{} OS is not supported".format(platform))