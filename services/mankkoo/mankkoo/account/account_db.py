import mankkoo.util.config as config
from mankkoo.base_logger import log
import pandas as pd


def load_all_accounts() -> dict:
    log.info("Loading all accounts...")
    return config.load_user_config()['accounts']['definitions']


def load_all_operations_as_df() -> pd.DataFrame:
    log.info('Loading ACCOUNT file...')
    df = pd.read_csv(
        config.mankkoo_file_path('account'),
        parse_dates=['Date'],
        index_col=0,
        encoding='iso-8859-2')
    if df.empty:
        return df
    df = df.astype({'Account': 'string', 'Balance': 'float', 'Operation': 'float', 'Date': 'datetime64[ns]'})
    df['Date'] = df['Date'].dt.date
    return df


def load_all_operations_as_dict() -> dict:
    user_config = config.load_user_config()
    df = __load_and_format_all_operations()

    accounts = user_config['accounts']['definitions']
    formatted_accounts = []

    for acc in accounts:
        acc_name = str(acc['bank']) + ' - ' + str(acc['name'])
        if __account_is_inactive(user_config, acc, acc_name):
            continue

        single_account = df[df['id'] == acc['id']]
        formatted_accounts.append(single_account)

    return pd.concat(formatted_accounts).to_dict('records')


def __load_and_format_all_operations() -> pd.DataFrame:
    df = load_all_operations_as_df()
    df = df.iloc[::-1]

    df = df[['Account', 'Date', 'Title', 'Details', 'Operation', 'Balance', 'Currency', 'Comment']]
    df = df.rename(columns={
            'Account': 'id',
            'Date': 'date',
            'Title': 'title',
            'Details': 'details',
            'Operation': 'operation',
            'Balance': 'balance',
            'Currency': 'currency',
            'Comment': 'comment'
        })
    df = df.fillna('')
    return df


def __account_is_inactive(user_config, acc, acc_name):
    return acc_name in user_config['accounts']['ui']['hide_accounts'] or acc['active'] is False
