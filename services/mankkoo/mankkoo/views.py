from datetime import date
from decimal import Decimal
import json

import mankkoo.database as db

from mankkoo.base_logger import log

main_indicators_key = 'main-indicators'
current_savings_distribution_key = 'current-savings-distribution'
total_history_per_day_key = 'total-history-per-day'

investment_indicators_key = 'investment-indicators'


def load_view(view_name):
    log.info(f"Loading '{view_name}' view...")
    query = f"""
    SELECT
        content
    FROM
        views
    WHERE name = '{view_name}';
    """

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
            if result is None:
                return None
            else:
                (view, ) = result

    return view


def update_views(oldest_occured_event_date: date):
    log.info(f'Updating views... (input: {oldest_occured_event_date})')
    __main_indicators()
    __current_total_savings_distribution()
    __total_history_per_day(oldest_occured_event_date)
    __investment_indicators()


def __main_indicators() -> None:
    log.info(f"Updating '{main_indicators_key}' view...")
    current_total_savings = __load_current_total_savings()

    view_content = {
        'savings': current_total_savings,
        'debt': None,
        'lastMonthProfit': 0,
        'investments': None
    }
    __store_view(main_indicators_key, view_content)
    log.info(f"The '{main_indicators_key}' view was updated")


def __load_current_total_savings() -> float:
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


def __current_total_savings_distribution():
    log.info(f"Updating '{current_savings_distribution_key}' view...")
    view_content = __load_current_total_savings_distribution()

    __store_view(current_savings_distribution_key, view_content)
    log.info(f"The '{current_savings_distribution_key}' view was updated")


def __load_current_total_savings_distribution() -> list[dict]:
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
        AND metadata ->> 'accountType' != 'cash'
        AND (metadata ->> 'active')::boolean = true
    ),

    accounts_balance AS (
        SELECT
            SUM((data->>'balance')::numeric) AS total,
            CASE
                WHEN l.type = 'checking' THEN 'Checking Accounts'
                WHEN l.type = 'savings' THEN 'Savings Accounts'
            ELSE l.type
            END AS type
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
             'Retirement' as type
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
            SUM((data->>'balance')::numeric) AS total,
            'Investments' AS type
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
            'Stocks & ETFs' AS type
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
    ORDER BY
        array_position(ARRAY['Checking Accounts', 'Savings Accounts', 'Investments', 'Stocks & ETFs', 'Retirement'], type);
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


def __total_history_per_day(oldest_occured_event_date: date):
    log.info(f"Updating '{total_history_per_day_key}' view...")
    view_content = __load_total_history_per_day(oldest_occured_event_date)

    __store_view(total_history_per_day_key, view_content)
    log.info(f"The '{total_history_per_day_key}' view was updated")


def __load_total_history_per_day(oldest_occured_event_date: date) -> dict[str, list]:
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
                result["date"].append(row[0].strftime('%Y-%m-%d'))
                result["total"].append(row[1])
    return result


def __investment_indicators() -> None:
    log.info(f"Updating '{investment_indicators_key}' view...")
    log.info("Loading current total savings value...")
    query = """
    WITH
    
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

    view_content = {
        'totalInvestments': 0 if result is None else result,
        'lastYearTotalResultsValue': 0,
        'lastYearTotalResultsPercentage': 0,
        'resultsVsInflation': 0
    }
    __store_view(investment_indicators_key, view_content)
    log.info(f"The '{investment_indicators_key}' view was updated")


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def __store_view(view_name: str, view_content):
    json_string = json.dumps(view_content, cls=JSONEncoder)

    insert_statement = f"""
    INSERT INTO
        views (name, content)
    VALUES
        ('{view_name}', '{json_string}'::jsonb)
    ON CONFLICT
        (name)
    DO UPDATE
        SET content = '{json_string}'::jsonb, updated_at = now();
    """
    db.execute(insert_statement)
