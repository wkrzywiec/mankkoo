from apiflask import Schema
from apiflask.fields import Boolean, Float, String

import mankkoo.database as db
from mankkoo.account.models import Bank
from mankkoo.base_logger import log


class Account(Schema):
    id = String()
    name = String()
    number = String()
    alias = String()
    type = String()
    importer = String()
    active = Boolean()
    bankName = String()
    bankUrl = String()
    hidden = Boolean()
    openedAt = String()


def load_all_accounts() -> list[Account]:
    log.info("Loading all accounts...")
    query = """
    SELECT
        id,
        name,
        metadata->>'accountNumber' AS number,
        metadata->>'alias' AS alias,
        subtype AS type,
        metadata->>'importer' AS importer,
        active,
        bank AS bankName,
        metadata->>'bankUrl' AS bankUrl,
        false as hidden,
        (SELECT DATE(e.occured_at)
            FROM events e
            WHERE e.stream_id = s.id
            AND e.version = 1
            LIMIT 1) AS openedAt
    FROM streams s
    WHERE s.type = 'account'
    AND active = true
    ORDER BY bankName, name;
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
                account.openedAt = row[10]

                result.append(account)
    return result


def get_bank_type(account_id: str) -> Bank:
    log.info(f"Looking for bank enum for account_id {account_id}...")
    query = f"""
    SELECT
        metadata->>'importer' AS importer
    FROM streams
    WHERE id = '{account_id}'
    AND type = 'account';
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
            if result is None:
                raise ValueError(
                    f"Failed to load bank definition. There is no bank account definition with an id '{account_id}'"
                )
            else:
                (importer,) = result

    try:
        bank = Bank[importer]
        log.info(f"Found bank by account_id ({account_id}): {bank}")
        return bank
    except Exception:
        raise ValueError(
            f"Failed to load importer for bank. Importer with a code: '{importer}' is not known"
        )


def get_account_balance(account_id: str) -> float:
    log.info(f"Getting balance for an account: {account_id}...")
    query = f"""
    SELECT
        (data ->> 'balance')::numeric AS balance
    FROM
        events
    WHERE
        stream_id = '{account_id}'
    ORDER BY
        version DESC
    LIMIT 1;
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
            if result is None:
                return 0
            else:
                (balance,) = result
    return float(balance)


class AccountOperation(Schema):
    id = String()
    date = String()
    title = String()
    details = String()
    operation = Float()
    balance = Float()
    currency = String()
    comment = String()


def load_operations_for_account(stream_id: str) -> list[AccountOperation]:
    query = f"""
    SELECT
        id,
        occured_at::date AS date,
        data->>'title' AS title,
        data->>'details' AS details,
        data->>'amount' AS operation,
        data->>'balance' AS balance,
        data->>'currency' AS currency,
        '' AS comment
    FROM events
    WHERE stream_id = '{stream_id}'
    ORDER BY occured_at DESC
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
