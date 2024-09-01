import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import mankkoo.database as db
from mankkoo.base_logger import log


def current_total_savings() -> float:
    log.info("Loading current total savings value...")
    query = """
    WITH
    account_latest_version AS (
        SELECT
            id,
            version,
            metadata ->> 'accountName' as name,
            metadata ->> 'accountType' as type
        FROM streams
        WHERE type = 'account'
        AND (metadata ->> 'active')::boolean = true
    ),

    accounts_balance AS (
        SELECT
            SUM((data->>'balance')::numeric) AS total,
            l.type as type
        FROM
            events e
        JOIN
            account_latest_version l ON e.stream_id = l.id AND l.version = e.version
        GROUP BY
            l.type
        ),

    retirement_latest_version AS (
        SELECT
            id,
            version,
            metadata ->> 'accountName' as name,
            metadata ->> 'accountType' as type
        FROM
            streams
        WHERE
            type = 'retirement'
        AND
            (metadata ->> 'active')::boolean = true
    ),

    retirement_balance AS (
        SELECT
            SUM((data->>'balance')::numeric) AS total,
             'retirement' as type
        FROM
            events e
        JOIN
            retirement_latest_version l ON e.stream_id = l.id AND l.version = e.version
    ),

    investment_latest_version AS (
        SELECT
            id,
            version, metadata ->> 'investmentName' as name,
            metadata ->> 'category' as type
        FROM
            streams
        WHERE
            type = 'investment'
        AND
            (metadata ->> 'active')::boolean = true
    ),

    investment_balance AS (
        SELECT
            (data->>'balance')::numeric AS total,
            l.type
        FROM events e
        JOIN investment_latest_version l ON e.stream_id = l.id AND l.version = e.version
    ),


    stocks_latest_version AS (
        SELECT id, version
        FROM streams
        WHERE type = 'stocks'
    ),

    stocks_balance AS (
        SELECT
            ROUND(SUM((data->>'balance')::numeric), 2) AS total,
            'stocks' AS type
        FROM
            events e
        JOIN
            stocks_latest_version l ON e.stream_id = l.id AND l.version = e.version
    ),

    all_buckets AS (
        SELECT *
        FROM accounts_balance
            UNION
        SELECT *
        FROM retirement_balance
            UNION
        SELECT *
        FROM investment_balance
            UNION
        SELECT *
        FROM stocks_balance
    )

    SELECT SUM(total)
    FROM all_buckets;
    """

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            (result, ) = cur.fetchone()
    return 0 if result is None else result


def current_total_savings_distribution() -> list[dict]:
    log.info("Loading current savings distribution by type...")
    query = """
    WITH
    account_latest_version AS (
        SELECT
            id,
            version,
            metadata ->> 'accountName' as name,
            metadata ->> 'accountType' as type
        FROM streams
        WHERE type = 'account'
        AND (metadata ->> 'active')::boolean = true
    ),

    accounts_balance AS (
        SELECT
            SUM((data->>'balance')::numeric) AS total,
            l.type as type
        FROM
            events e
        JOIN
            account_latest_version l ON e.stream_id = l.id AND l.version = e.version
        GROUP BY
            l.type
        ),

    retirement_latest_version AS (
        SELECT
            id,
            version,
            metadata ->> 'accountName' as name,
            metadata ->> 'accountType' as type
        FROM
            streams
        WHERE
            type = 'retirement'
        AND
            (metadata ->> 'active')::boolean = true
    ),

    retirement_balance AS (
        SELECT
            SUM((data->>'balance')::numeric) AS total,
             'retirement' as type
        FROM
            events e
        JOIN
            retirement_latest_version l ON e.stream_id = l.id AND l.version = e.version
    ),

    investment_latest_version AS (
        SELECT
            id,
            version, metadata ->> 'investmentName' as name,
            metadata ->> 'category' as type
        FROM
            streams
        WHERE
            type = 'investment'
        AND
            (metadata ->> 'active')::boolean = true
    ),

    investment_balance AS (
        SELECT
            (data->>'balance')::numeric AS total,
            'investments' AS type
        FROM events e
        JOIN investment_latest_version l ON e.stream_id = l.id AND l.version = e.version
    ),


    stocks_latest_version AS (
        SELECT id, version
        FROM streams
        WHERE type = 'stocks'
    ),

    stocks_balance AS (
        SELECT
            ROUND(SUM((data->>'balance')::numeric), 2) AS total,
            'stocks' AS type
        FROM
            events e
        JOIN
            stocks_latest_version l ON e.stream_id = l.id AND l.version = e.version
    ),

    all_buckets AS (
        SELECT *
        FROM accounts_balance
            UNION
        SELECT *
        FROM retirement_balance
            UNION
        SELECT *
        FROM investment_balance
            UNION
        SELECT *
        FROM stocks_balance
    )

    SELECT
        type,
        total,
        round(
            total
            /
            (SELECT SUM(total) FROM all_buckets)
            , 4) as percentage
    FROM all_buckets
    ORDER BY type='retirement', type='stocks', type='cash', type='savings', type='checking';
    """

    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                savings = {
                    "type": row[0],
                    "total": row[1],
                    "percentage": row[2]
                }
                result.append(savings)
    return result


def total_history_per_day(oldest_occured_event_date: datetime.date) -> dict[str, list]:
    log.info("Loading total history per day starting from oldest occured event date...")
    query = """
    WITH date_range AS (
    SELECT
        (SELECT MIN(occured_at) FROM events) AS from_date,  -- Start date (earliest event date)
        (SELECT MAX(occured_at) FROM events) AS till_date -- End date (latest event date)
    ),

    date_series AS (
    SELECT
    generate_series(
            date_range.from_date,
            date_range.till_date,
            '1 day'::interval
    )::date AS occured_at
    FROM date_range
    ),

    all_day_and_accounts AS (
    SELECT
        date_series.occured_at,
        stream_ids.id AS stream_id
    FROM
        date_series
    CROSS JOIN (SELECT id FROM streams) stream_ids
    ORDER BY
        stream_ids.id, date_series.occured_at
    ),

    all_account_balances_per_day AS (
    SELECT al.occured_at, al.stream_id,
       COALESCE((
           SELECT events.data ->> 'balance'
           FROM events
           WHERE events.stream_id = al.stream_id
             AND events.occured_at <= al.occured_at
           ORDER BY events.version DESC
           LIMIT 1
       )::numeric, 0) AS balance
    FROM all_day_and_accounts al
    )

    SELECT
        occured_at,
        SUM(balance) as balance
    FROM
        all_account_balances_per_day
    LEFT JOIN streams ON all_account_balances_per_day.stream_id = streams.id
    GROUP BY
        occured_at
    ORDER BY
        occured_at DESC;
    """

    result = {
        "date": [],
        "total": []
    }
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                # day = {
                #     row[0].strftime('%Y-%m-%d'): row[1]
                # }
                result["date"].append(row[0].strftime('%Y-%m-%d'))
                result["total"].append(row[1])
    return result
