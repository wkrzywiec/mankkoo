import os
import pathlib
from sys import platform
import logging as log
import app.scripts.data as data
import pandas as pd

mankkoo_dir = '.mankkoo'
account_file = 'account.csv'

def init_data_folder():
    """Initilize .mankkoo directory in home folder and account.csv file inside of it
    """
    mankkoo_path = mankoo_path()
    mankoo_account_file = mankoo_account_path()

    log.info('Initializing mankkoo directory and files')

    if not os.path.exists(mankkoo_path):
        log.info('Creating mankkoo directory')
        os.makedirs(mankkoo_path)

    if not os.path.exists(mankoo_account_file):
        log.info("Creating mankkoo's account file")
        df = pd.DataFrame(columns=data.columns)
        df.to_csv(mankoo_account_file)

def mankoo_account_path():
    """Get a full path to the account.csv file

    Returns:
        str: full path to account.csv file
    """
    return mankoo_path() + __slash() + account_file

def mankoo_path():
    """Get full path to the .mankkoo directory

    Returns:
        str: full path to .mankkoo directory
    """
    return os.path.expanduser("~") + __slash() + mankkoo_dir

def __slash():
    if platform == "linux":
        return "/"
    elif platform == "win32":
        return "\\"
    elif platform == "darwin":
        raise ValueError("MacOS is currently not supported")

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