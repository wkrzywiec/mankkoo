import json
from datetime import date
from decimal import Decimal

import mankkoo.database as db
from mankkoo.base_logger import log

main_indicators_key = "main-indicators"
current_savings_distribution_key = "current-savings-distribution"
total_history_per_day_key = "total-history-per-day"

investment_indicators_key = "investment-indicators"
investment_types_distribution_key = "investment-types-distribution"
investment_wallets_distribution_key = "investment-wallets-distribution"
investment_types_distribution_per_wallet_key = (
    "investment-types-distribution-per-wallet"
)


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
                (view,) = result

    return view


def update_views(oldest_occured_event_date: date):
    log.info(f"Updating views... (input: {oldest_occured_event_date})")
    __main_indicators()
    __current_total_savings_distribution()
    __total_history_per_day(oldest_occured_event_date)
    __investment_indicators()
    __investment_types_distribution()
    __investment_wallets_distribution()
    __investment_types_distribution_per_wallet()


def __main_indicators() -> None:
    log.info(f"Updating '{main_indicators_key}' view...")
    current_total_savings = __load_current_total_savings()

    view_content = {
        "savings": current_total_savings,
        "netWorth": None,
        "lastMonthIncome": None,
        "lastMonthSpending": None,
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
            name,
            subtype
        FROM streams
        WHERE type = 'account'
        AND active = true
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
            name,
            subtype
        FROM
            streams
        WHERE
            type = 'retirement'
        AND
            active = true
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
            version, name,
            subtype
        FROM
            streams
        WHERE
            type = 'investment'
        AND
            active = true
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
            (result,) = cur.fetchone()
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
            name,
            subtype
        FROM streams
        WHERE type = 'account'
        AND subtype != 'cash'
        AND active = true
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
            name,
            subtype
        FROM
            streams
        WHERE
            type = 'retirement'
        AND
            active = true
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
            version, name,
            subtype
        FROM
            streams
        WHERE
            type = 'investment'
        AND
            active = true
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
                savings = {"type": row[0], "total": row[1], "percentage": row[2]}
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

    result = {"date": [], "total": []}
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                result["date"].append(row[0].strftime("%Y-%m-%d"))
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
            version, name,
            subtype
        FROM
            streams
        WHERE
            type = 'investment'
        AND
            active = true
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
        AND active = true
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
    savings_latest_version AS (
        SELECT id, version
        FROM streams
        WHERE type = 'account'
          AND (subtype) = 'savings'
          AND active = true
    ),
    savings_balance AS (
        SELECT
            SUM((data->>'balance')::numeric) AS total,
            'savings' AS type
        FROM events e
        JOIN savings_latest_version l ON e.stream_id = l.id AND l.version = e.version
    ),
    all_buckets AS (
        SELECT * FROM investment_balance
            UNION
        SELECT * FROM stocks_balance
            UNION
        SELECT * FROM savings_balance
    )
    SELECT SUM(total)
    FROM all_buckets;
    """

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            (result,) = cur.fetchone()

    view_content = {
        "totalInvestments": 0 if result is None else result,
        "lastYearTotalResultsValue": 0,
        "lastYearTotalResultsPercentage": 0,
        "resultsVsInflation": 0,
    }
    __store_view(investment_indicators_key, view_content)
    log.info(f"The '{investment_indicators_key}' view was updated")


def __investment_types_distribution():
    log.info(f"Updating '{investment_types_distribution_key}' view...")
    view_content = __load_investment_types_distribution()
    __store_view(investment_types_distribution_key, view_content)
    log.info(f"The '{investment_types_distribution_key}' view was updated")


def __load_investment_types_distribution() -> list[dict]:
    log.info(
        "Loading investment types distribution by type (including savings accounts)..."
    )
    query = """
    WITH investment_streams AS (
        SELECT id, version, subtype
        FROM streams
        WHERE type = 'investment'
          AND active = true
    ),
    investment_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.type
        FROM events e
        JOIN investment_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.type
    ),
    stocks_streams AS (
        SELECT id, version, subtype
        FROM streams
        WHERE type = 'stocks'
          AND active = true
    ),
    stocks_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.type
        FROM events e
        JOIN stocks_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.type
    ),
    savings_streams AS (
        SELECT id, version, 'Savings Accounts' AS type
        FROM streams
        WHERE type = 'account'
          AND (subtype) = 'savings'
          AND active = true
    ),
    savings_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.type
        FROM events e
        JOIN savings_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.type
    ),
    all_types AS (
        SELECT * FROM investment_balance
        UNION ALL
        SELECT * FROM stocks_balance
        UNION ALL
        SELECT * FROM savings_balance
    )
    SELECT
        type,
        total,
        ROUND(total / NULLIF((SELECT SUM(total) FROM all_types), 0), 4) AS percentage
    FROM all_types
    ORDER BY total DESC;
    """

    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                result.append(
                    {
                        "type": (
                            row[0].replace("_", " ").title()
                            if row[0] != "Savings Accounts"
                            else row[0]
                        ),
                        "total": row[1],
                        "percentage": row[2],
                    }
                )
    return result


def __investment_wallets_distribution():
    log.info(f"Updating '{investment_wallets_distribution_key}' view...")
    view_content = __load_investment_wallets_distribution()
    __store_view(investment_wallets_distribution_key, view_content)
    log.info(f"The '{investment_wallets_distribution_key}' view was updated")


def __load_investment_wallets_distribution() -> list[dict]:
    log.info(
        "Loading investment distribution by wallet (including savings accounts, merged by wallet)..."
    )
    query = """
    WITH investment_streams AS (
        SELECT id, version, labels ->> 'wallet' AS wallet
        FROM streams
        WHERE type = 'investment'
          AND active = true
    ),
    investment_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.wallet
        FROM events e
        JOIN investment_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.wallet
    ),
    stocks_streams AS (
        SELECT id, version, labels ->> 'wallet' AS wallet
        FROM streams
        WHERE type = 'stocks'
          AND active = true
    ),
    stocks_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.wallet
        FROM events e
        JOIN stocks_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.wallet
    ),
    savings_streams AS (
        SELECT id, version, labels ->> 'wallet' AS wallet
        FROM streams
        WHERE type = 'account'
          AND (subtype) = 'savings'
          AND active = true
    ),
    savings_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.wallet
        FROM events e
        JOIN savings_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.wallet
    ),
    all_wallets_raw AS (
        SELECT wallet, total FROM investment_balance
        UNION ALL
        SELECT wallet, total FROM stocks_balance
        UNION ALL
        SELECT wallet, total FROM savings_balance
    ),
    all_wallets AS (
        SELECT wallet, SUM(total) AS total
        FROM all_wallets_raw
        GROUP BY wallet
    )
    SELECT
        wallet,
        total,
        ROUND(total / NULLIF((SELECT SUM(total) FROM all_wallets), 0), 4) AS percentage
    FROM all_wallets
    ORDER BY total DESC;
    """

    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                result.append({"wallet": row[0], "total": row[1], "percentage": row[2]})
    return result


def __investment_types_distribution_per_wallet():
    log.info("Updating 'investment-types-distribution-per-wallet' view...")
    view_content = __load_investment_types_distribution_per_wallet()
    __store_view("investment-types-distribution-per-wallet", view_content)
    log.info("The 'investment-types-distribution-per-wallet' view was updated")


def __load_investment_types_distribution_per_wallet() -> list[dict]:
    log.info(
        "Loading investment type distribution per wallet (including savings accounts)..."
    )
    query = """
    WITH investment_streams AS (
        SELECT id, version, labels ->> 'wallet' AS wallet, subtype
        FROM streams
        WHERE type = 'investment' AND active = true
    ),
    investment_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.wallet,
            s.type
        FROM events e
        JOIN investment_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.wallet, s.type
    ),
    stocks_streams AS (
        SELECT id, version, labels ->> 'wallet' AS wallet, subtype
        FROM streams
        WHERE type = 'stocks' AND active = true
    ),
    stocks_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.wallet,
            s.type
        FROM events e
        JOIN stocks_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.wallet, s.type
    ),
    savings_streams AS (
        SELECT id, version, labels ->> 'wallet' AS wallet, 'Savings Accounts' AS type
        FROM streams
        WHERE type = 'account' AND (subtype) = 'savings' AND active = true
    ),
    savings_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.wallet,
            s.type
        FROM events e
        JOIN savings_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.wallet, s.type
    ),
    all_types AS (
        SELECT * FROM investment_balance
        UNION ALL
        SELECT * FROM stocks_balance
        UNION ALL
        SELECT * FROM savings_balance
    ),
    wallet_totals AS (
        SELECT wallet, SUM(total) AS wallet_total
        FROM all_types
        GROUP BY wallet
    )
    SELECT
        a.wallet,
        a.type,
        a.total,
        ROUND(a.total / NULLIF(w.wallet_total, 0), 4) AS percentage
    FROM all_types a
    JOIN wallet_totals w ON a.wallet = w.wallet
    ORDER BY a.wallet, a.total DESC;
    """
    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                result.append(
                    {
                        "wallet": row[0],
                        "type": (
                            row[1].replace("_", " ").title()
                            if row[1] != "Savings Accounts"
                            else row[1]
                        ),
                        "total": row[2],
                        "percentage": row[3],
                    }
                )
    return result


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
