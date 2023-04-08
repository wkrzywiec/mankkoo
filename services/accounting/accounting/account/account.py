import pandas as pd
import accounting.account.importer.importer as importer
import accounting.account.account_db as db
import accounting.account.models as models
import accounting.util.config as config
import accounting.total.total as total
from accounting.base_logger import log

log.basicConfig(level=log.DEBUG)

def add_new_operations(account_id: str, file_name=None, contents=None) -> pd.DataFrame:
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
    log.info('Adding new operations for %s account', account_id)
    bank = __get_bank_type(account_id)
    df_new = importer.load_bank_data(file_name, contents, bank, account_id)
    df = db.load_all_operations_as_df()
    __make_account_backup(df)

    df = pd.concat([df, df_new]).reset_index(drop=True)
    df = df.sort_values(by=['Date', 'Account'])
    df = df.reset_index(drop=True)
    df = calculate_balance(df, account_id)
    df.to_csv(config.mankkoo_file_path('account'), index=True, index_label='Row')

    total.update_total_money(df, df_new['Date'].min())
    total.update_monthly_profit(from_date=df_new['Date'].min(), force=True)
    log.info('%d new operations for %s account were added.', df_new['Account'].size, account_id)
    return df

def calculate_balance(df: pd.DataFrame, account_id: str) -> pd.DataFrame:
    """Calculates balance for new operations

    Args:
        df (pandas.DataFrame): DataFrame with a column 'Balance' which has some rows with value NaN

    Returns:
        pandas.DataFrame: DataFrame with calucated 'Balance' after each operation
    """
    log.info('Calculating balance for %s account.', account_id)
    # TODO move to importer.py
    df = df.astype({'Balance': 'float', 'Operation': 'float'})
    non_balanced_rows = df['Balance'].index[df['Balance'].apply(pd.isna)]

    latest_balance = __latest_balance_for_account(df, account_id)

    log.info('Calculating balance for %s account from %s', account_id, df.iloc[non_balanced_rows[0]]['Date'])
    for i in non_balanced_rows.values.tolist():
        latest_balance = latest_balance + df.loc[i, 'Operation']
        df.loc[i, 'Balance'] = round(latest_balance, 2)

    return df

def __get_bank_type(account_id: str):
    account_defs = config.load_user_config()['accounts']['definitions']
    account_list = [acc for acc in account_defs if acc['id'] == account_id]
    
    if len(account_list) == 0:
        raise ValueError(f"Failed to load bank definition. There is no bank account definition with an id '{account_id}'")

    importer = account_list[0]['importer']
    
    try:
        bank = models.Bank[importer]
        log.info(f"Found bank by account_id ({account_id}): {bank}")
        return bank
    except Exception as ex:
        raise ValueError(f"Failed to load importer for bank. Importer with a code: '{importer}' is not known")

def __latest_balance_for_account(df: pd.DataFrame, account_id: str):

    result = df.loc[(df['Account'] == account_id)]
    result = result.dropna(subset=['Balance'])
    try:
        return result.iloc[-1]['Balance']
    except IndexError:
        log.info('There are no latest balance for %s account. Therefore assuming 0.', account_id)
        return 0

def __make_account_backup(df: pd.DataFrame):
    df.to_csv(config.mankkoo_file_path('account-backup'), index=True)
