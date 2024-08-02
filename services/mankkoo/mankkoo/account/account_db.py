import pandas as pd
import mankkoo.util.config as config
import mankkoo.database as db

from mankkoo.base_logger import log
from mankkoo.controller.account_controller import Account, AccountOperation


def load_all_accounts() -> list[Account]:
    log.info("Loading all accounts...")
    query = """
    SELECT
        id,
        metadata->>'accountName' AS name,
        metadata->>'accountNumber' AS number,
        metadata->>'alias' AS alias,
        metadata->>'accountType' AS type,
        metadata->>'importer' AS importer,
        metadata->>'active' AS active,
        metadata->>'bankName' AS bankName,
        metadata->>'bankUrl' AS bankUrl,
        false as hidden
    FROM streams
    WHERE type = 'account'
    AND (metadata ->> 'active')::boolean = true;
    """

    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                account = Account()
                account.id = row[0]
                account.name = row[1]
                account.number = row[2]
                account.alias = row[3]
                account.type = row[4]
                account.importer = row[5]
                account.active = row[6]
                account.bankName = row[7]
                account.bankUrl = row[8]
                account.hidden = row[9]

                result.append(account)
    return result


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


def load_operations_for_account_as_dict(stream_id: str) -> list[AccountOperation]:

    query = f"""
    SELECT
        id,
        occured_at AS date,
        data->>'title' AS title,
        data->>'details' AS details,
        data->>'amount' AS operation,
        data->>'balance' AS balance,
        data->>'currency' AS currency,
        '' AS comment
    FROM events
    WHERE stream_id = '{stream_id}'
    ORDER BY occured_at
    """

    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                operation = AccountOperation()
                operation.id = row[0]
                operation.date = row[1]
                operation.title = row[2]
                operation.details = row[3]
                operation.operation = row[4]
                operation.balance = row[5]
                operation.currency = row[6]
                operation.comment = row[7]

                result.append(operation)
    return result


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
