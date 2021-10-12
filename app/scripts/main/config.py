import os
import pathlib
import yaml
from sys import platform
from scripts.main.base_logger import log
import scripts.main.data as data
import pandas as pd

mankkoo_dir = '.mankkoo'
account_file = 'account.csv'
investment_file = 'investment.csv'
stock_file = 'stock.csv'
total_file = 'total.csv'

mankkoo_files = {account_file, investment_file, stock_file, total_file}

def init_data_folder():
    """Initilize .mankkoo directory in home folder and account.csv file inside of it
    """
    mankkoo_path = mankoo_path()
    mankoo_account_file = mankoo_file_path('account')

    log.info("Checking if mankkoo's files are existing")

    if not os.path.exists(mankkoo_path):
        log.info('Creating mankkoo directory')
        os.makedirs(mankkoo_path)

    for file in mankkoo_files:
        file_path = mankoo_file_path(file)
        if not os.path.exists(file_path):
            log.info("Creating mankkoo's " + file + " file")
            df = pd.DataFrame(columns=__select_columns(file))
            df.to_csv(file_path, index=False)

def __select_columns(file: str):
    if file == account_file:
        return data.account_columns
    if file == investment_file:
        return data.invest_columns
    if file == stock_file:
        return data.stock_columns
    if file == total_file:
        return data.total_columns

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

    if file in {'account', 'account-backup', 'investment', 'stock', 'total'}:
        return path + file + '.csv'

    if file in mankkoo_files:
        return path + file

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

def load_config_file():
    log.info('Loading config.yaml file')
    with open(data_path() + 'config.yaml') as c:
        return yaml.safe_load(c)
