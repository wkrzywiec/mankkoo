import pandas as pd
import scripts.main.importer.importer as importer
import scripts.main.models as models
import scripts.main.config as config
import scripts.main.total as total
from scripts.main.base_logger import log

log.basicConfig(level=log.DEBUG)

account_columns = ['Bank', 'Type', 'Account', 'Date', 'Title', 'Details', 'Category', 'Comment', 'Operation', 'Currency', 'Balance']
invest_columns = ['Active', 'Category', 'Bank', 'Investment', 'Start Date', 'End Date', 'Start Amount', 'End amount', 'Currency', 'Details', 'Comment']
stock_columns = ['Broker', 'Date', 'Title', 'Operation', 'Total Value', 'Units', 'Currency', 'Details', 'Url', 'Comment']
total_columns = ['Date', 'Total']


def load_data() -> dict:
    """Load aggregated data of all financial data (accounts, investments, etc.)

    Returns:
        dict(pandas.DataFrame): a dictonary with categorized financial data
    """
    log.info("Loading mankkoo's files")

    return dict(
        account=importer.load_data_from_file(models.FileType.ACCOUNT),
        investment=importer.load_data_from_file(models.FileType.INVESTMENT),
        stock=importer.load_data_from_file(models.FileType.STOCK),
        total=importer.load_data_from_file(models.FileType.TOTAL)
    )

def add_new_operations(bank: models.Bank, account_name: str, file_name=None, contents=None) -> pd.DataFrame:
    """Append bank accounts history with new operations. 
    This method return a pandas DataFrame with calculated balance.

    Args:
        bank (importer.Bank): enum of a bank company
        file_name (str): name of a file from which data will be loaded

    Raises:
        KeyError: raised when unsupported bank enum is provided

    Returns:
        pandas.DataFrame: DataFrame that holds transactions history with newly added operations
    """
    log.info('Adding new operations for %s account in %s bank', account_name, bank)
    df_new = importer.load_bank_data(file_name, contents, bank, account_name)
    df = importer.load_data_from_file(models.FileType.ACCOUNT)
    __make_account_backup(df)

    df = pd.concat([df, df_new]).reset_index(drop=True)
    df = df.sort_values(by=['Date', 'Bank', 'Account'])
    df = df.reset_index(drop=True)
    df = calculate_balance(df, account_name)
    df.to_csv(config.mankkoo_file_path('account'), index=True, index_label='Row')

    total.update_total_money(df, df_new['Date'].min())
    log.info('%d new operations for %s account were added.', df_new['Bank'].size, account_name)
    return df

def calculate_balance(df: pd.DataFrame, account_name: str) -> pd.DataFrame:
    """Calculates balance for new operations

    Args:
        df (pandas.DataFrame): DataFrame with a column 'Balance' which has some rows with value NaN

    Returns:
        pandas.DataFrame: DataFrame with calucated 'Balance' after each operation
    """
    log.info('Calculating balance for %s account.', account_name)
    # TODO move to importer.py
    df = df.astype({'Balance': 'float', 'Operation': 'float'})
    non_balanced_rows = df['Balance'].index[df['Balance'].apply(pd.isna)]

    latest_balance = __latest_balance_for_account(df, account_name)

    log.info('Calculating balance for %s account from %s', account_name, df.iloc[non_balanced_rows[0]]['Date'])
    for i in range(non_balanced_rows[0], len(df)):
        latest_balance = latest_balance + df.loc[i, 'Operation']
        df.loc[i, 'Balance'] = round(latest_balance, 2)

    return df

def __latest_balance_for_account(df: pd.DataFrame, account_name: str):

    result = df.loc[(df['Account'] == account_name)]
    result = result.dropna(subset=['Balance'])
    try:
        return result.iloc[-1]['Balance']
    except IndexError:
        log.info('There are no latest balance for %s account. Therefore assuming 0.', account_name)
        return 0

def __make_account_backup(df: pd.DataFrame):
    df.to_csv(config.mankkoo_file_path('account-backup'), index=False)
