import os
import pathlib
import yaml
from sys import platform
from scripts.main.base_logger import log
import scripts.main.database as db
import pandas as pd

mankkoo_dir = '.mankkoo'
account_file = 'account.csv'
investment_file = 'investment.csv'
stock_file = 'stock.csv'
total_file = 'total.csv'
total_monthly_file = 'total_monthly.csv'
config_file = 'config.yaml'

mankkoo_files = {account_file, investment_file, stock_file, total_file, total_monthly_file}

def init_data_folder():
    """Initilize .mankkoo directory in home folder, config file and all storage files
    """
    m_path = mankkoo_path()

    log.info("Checking if mankkoo's files are existing...")

    if not os.path.exists(m_path):
        log.info('Creating mankkoo directory...')
        os.makedirs(m_path)

    for file in mankkoo_files:
        file_path = mankkoo_file_path(file)
        if not os.path.exists(file_path):
            log.info("Creating mankkoo's " + file + " file...")
            df = pd.DataFrame(columns=__select_columns(file))
            df.to_csv(file_path, index=False)
            log.info(f"{file} was created in .mankkoo directory")

    if not os.path.exists(m_path + __slash() + config_file):
        log.info(f"Creating user {config_file} file...")
        config_d = dict(
            accounts=dict(
                definitions=[],
                ui=dict(
                    default_importer='',
                    hide_accounts=[]
                )
            )
        )

        save_user_config(config_d)
        log.info(f"User {config_file} file was created in .mankkoo directory")

def __select_columns(file: str):
    if file == account_file:
        return db.account_columns
    if file == investment_file:
        return db.invest_columns
    if file == stock_file:
        return db.stock_columns
    if file == total_file:
        return db.total_columns
    if file == total_monthly_file:
        return db.total_monthly_columns

def mankkoo_file_path(file: str) -> str:
    """Get full path of one of mankkoo's files.

    Args:
        file (str): Which file needs to be loaded. Supported values: 'account', 'investment' and 'stock'

    Raises:
        ValueError: raised when invalid file type has been provided

    Returns:
        str: full path to the mankkoo's data file
    """
    path = mankkoo_path() + __slash()

    if file in {'account', 'account-backup', 'investment', 'stock', 'total', 'total_monthly'}:
        return path + file + '.csv'

    if file in mankkoo_files:
        return path + file

    raise ValueError("Can't get mankkoo file. Unsupported file type: {}".format(file))

def mankkoo_path() -> str:
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

def load_global_config() -> dict:
    """Load global configuration from /data folder

    Returns:
        dict: global specific config from config.yaml file
    """
    log.info(f"Loading global {config_file} file")
    with open(data_path() + config_file) as c:
        return yaml.safe_load(c)

def load_user_config() -> dict:
    """Load user configuration from .mankkoo directory

    Returns:
        dict: user specific config from config.yaml file
    """
    log.info(f"Loading user {config_file} file")
    with open(mankkoo_path() + __slash() + config_file, 'r', encoding='utf-8') as c:
        result = yaml.safe_load(c)
    
    accounts = result['accounts']['definitions']
    accounts_sorted = []
    keyorder = ['id', 'bank', 'name', 'alias', 'type', 'active', 'bank_url']

    for acc in accounts: 
        acc_sorted = {k: acc[k] for k in keyorder if k in acc}
        accounts_sorted.append(acc_sorted)
    
    result['accounts']['definitions'] = accounts_sorted

    return result

def save_user_config(user_config: dict):
    log.info(f"Saving user config file. New file: {user_config}")
    
    try:
        with open(mankkoo_path() + __slash() + config_file, 'w', encoding="utf-8") as outfile:
            yaml.dump(user_config, outfile, allow_unicode=True, default_flow_style=False)
    except Exception as err:
        log.info(err)

    log.info(f"User config file was updated in .mankkoo directory")
