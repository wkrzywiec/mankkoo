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

monthly_income_key = "monthly-income"

investment_deposited_vs_value_key = "investment-deposited-vs-value"
investment_deposited_vs_value_per_wallet_key = (
    "investment-deposited-vs-value-per-wallet"
)
investment_deposited_vs_value_history_key = "investment-deposited-vs-value-history"
investment_deposited_vs_value_history_per_wallet_key = (
    "investment-deposited-vs-value-history-per-wallet"
)
investment_deposited_vs_value_history_by_type_per_wallet_key = (
    "investment-deposited-vs-value-history-by-type-per-wallet"
)


def load_view(view_name):
    log.info(f"Loading '{view_name}' view...")
    query = """
    SELECT
        content
    FROM
        views
    WHERE name = %s;
    """

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (view_name,))
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
    __monthly_income()
    __investment_deposited_vs_value()
    __investment_deposited_vs_value_per_wallet()
    __investment_deposited_vs_value_history()
    __investment_deposited_vs_value_history_per_wallet()
    __investment_deposited_vs_value_history_by_type_per_wallet()


def __main_indicators() -> None:
    log.info(f"Updating '{main_indicators_key}' view...")
    current_total_savings = __load_current_total_savings()
    monthly_income_data = __load_monthly_income()
    last_month_income = (
        monthly_income_data["total"][-1] if monthly_income_data["total"] else None
    )

    view_content = {
        "savings": current_total_savings,
        "netWorth": None,
        "lastMonthIncome": last_month_income,
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
        AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),

    accounts_balance AS (
        SELECT
            SUM((data->>'balance')::numeric) AS total,
            l.subtype as type
        FROM
            events e
        JOIN
            account_latest_version l ON e.stream_id = l.id AND l.version = e.version
        GROUP BY
            l.subtype
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
        AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
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
        AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),

    investment_balance AS (
        SELECT
            (data->>'balance')::numeric AS total,
            l.subtype
        FROM events e
        JOIN investment_latest_version l ON e.stream_id = l.id AND l.version = e.version
    ),


    stocks_latest_version AS (
        SELECT id, version
        FROM streams
        WHERE type = 'stocks'
        AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
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
    if result is None:
        log.warning("Total savings calculation returned None, defaulting to 0")
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
        AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),

    accounts_balance AS (
        SELECT
            SUM((data->>'balance')::numeric) AS total,
            CASE
                WHEN l.subtype = 'checking' THEN 'Checking Accounts'
                WHEN l.subtype = 'savings' THEN 'Savings Accounts'
            ELSE l.subtype
            END AS type
        FROM
            events e
        JOIN
            account_latest_version l ON e.stream_id = l.id AND l.version = e.version
        GROUP BY
            l.subtype
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
        AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
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
        AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
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
        AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
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
            NULLIF((SELECT SUM(total) FROM all_buckets), 0)
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
    CROSS JOIN (SELECT id FROM streams WHERE labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true') stream_ids
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


def __load_monthly_income() -> dict[str, list]:
    log.info("Loading monthly income (last-day minus first-day balance per month)...")
    query = """
    WITH
    wealth_streams AS (
        SELECT id FROM streams
        WHERE labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true'
    ),

    month_series AS (
        SELECT generate_series(
            date_trunc('month', (SELECT MIN(occured_at) FROM events)),
            date_trunc('month', now()) - interval '1 month',
            '1 month'::interval
        )::date AS month_start
    ),

    first_day_balance AS (
        SELECT
            ms.month_start,
            ws.id AS stream_id,
            COALESCE((
                SELECT (e.data->>'balance')::numeric
                FROM events e
                WHERE e.stream_id = ws.id
                  AND e.occured_at <= ms.month_start
                ORDER BY e.version DESC
                LIMIT 1
            ), 0) AS balance
        FROM month_series ms
        CROSS JOIN wealth_streams ws
    ),

    last_day_balance AS (
        SELECT
            ms.month_start,
            ws.id AS stream_id,
            COALESCE((
                SELECT (e.data->>'balance')::numeric
                FROM events e
                WHERE e.stream_id = ws.id
                  AND e.occured_at <= (ms.month_start + interval '1 month - 1 day')::date
                ORDER BY e.version DESC
                LIMIT 1
            ), 0) AS balance
        FROM month_series ms
        CROSS JOIN wealth_streams ws
    )

    SELECT
        f.month_start,
        SUM(l.balance - f.balance) AS income
    FROM first_day_balance f
    JOIN last_day_balance l ON f.stream_id = l.stream_id AND f.month_start = l.month_start
    GROUP BY f.month_start
    ORDER BY f.month_start ASC;
    """

    result: dict[str, list] = {"date": [], "total": []}
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                result["date"].append(row[0].strftime("%Y-%m"))
                result["total"].append(row[1])
    return result


def __monthly_income() -> None:
    log.info(f"Updating '{monthly_income_key}' view...")
    view_content = __load_monthly_income()
    __store_view(monthly_income_key, view_content)
    log.info(f"The '{monthly_income_key}' view was updated")


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
        AND
            (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),
    investment_balance AS (
        SELECT
            (data->>'balance')::numeric AS total,
            l.subtype
        FROM events e
        JOIN investment_latest_version l ON e.stream_id = l.id AND l.version = e.version
    ),
    stocks_latest_version AS (
        SELECT id, version
        FROM streams
        WHERE type = 'stocks'
        AND active = true
        AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
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
          AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
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
          AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),
    investment_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.subtype
        FROM events e
        JOIN investment_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.subtype
    ),
    stocks_streams AS (
        SELECT id, version, subtype
        FROM streams
        WHERE type = 'stocks'
          AND active = true
          AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),
    stocks_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.subtype
        FROM events e
        JOIN stocks_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.subtype
    ),
    savings_streams AS (
        SELECT id, version, 'Savings Accounts' AS subtype
        FROM streams
        WHERE type = 'account'
          AND (subtype) = 'savings'
          AND active = true
          AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),
    savings_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.subtype
        FROM events e
        JOIN savings_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.subtype
    ),
    all_types AS (
        SELECT * FROM investment_balance
        UNION ALL
        SELECT * FROM stocks_balance
        UNION ALL
        SELECT * FROM savings_balance
    )
    SELECT
        subtype,
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
            s.subtype
        FROM events e
        JOIN investment_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.wallet, s.subtype
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
            s.subtype
        FROM events e
        JOIN stocks_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.wallet, s.subtype
    ),
    savings_streams AS (
        SELECT id, version, labels ->> 'wallet' AS wallet, 'Savings Accounts' AS subtype
        FROM streams
        WHERE type = 'account' AND (subtype) = 'savings' AND active = true
    ),
    savings_balance AS (
        SELECT
            SUM((e.data->>'balance')::numeric) AS total,
            s.wallet,
            s.subtype
        FROM events e
        JOIN savings_streams s ON e.stream_id = s.id AND e.version = s.version
        GROUP BY s.wallet, s.subtype
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
        a.subtype,
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


def __load_investment_deposited_vs_value() -> list[dict]:
    log.info("Loading investment deposited vs value by type...")
    query = """
    WITH wealth_streams AS (
        SELECT id, subtype
        FROM streams
        WHERE type IN ('investment', 'stocks')
          AND active = true
          AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),
    deposited AS (
        SELECT
            s.id,
            s.subtype,
            COALESCE(SUM(CASE WHEN e.type LIKE '%%Bought' OR e.type LIKE '%%Sold' OR e.type LIKE '%%Matured' THEN (e.data->>'totalValue')::numeric ELSE 0 END), 0) AS deposited
        FROM wealth_streams s
        JOIN events e ON e.stream_id = s.id
        GROUP BY s.id, s.subtype
    ),
    latest_balance AS (
        SELECT DISTINCT ON (e.stream_id)
            e.stream_id,
            (e.data->>'balance')::numeric AS value
        FROM events e
        JOIN wealth_streams s ON s.id = e.stream_id
        ORDER BY e.stream_id, e.version DESC
    ),
    combined AS (
        SELECT d.subtype, d.deposited, lb.value
        FROM deposited d
        JOIN latest_balance lb ON lb.stream_id = d.id
    )
    SELECT
        subtype,
        ROUND(SUM(deposited), 2) AS total_deposited,
        ROUND(SUM(value), 2) AS total_value
    FROM combined
    GROUP BY subtype
    ORDER BY total_value DESC;
    """
    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                result.append(
                    {
                        "type": row[0].replace("_", " ").title(),
                        "deposited": float(row[1] or 0),
                        "value": float(row[2] or 0),
                    }
                )
    return result


def __investment_deposited_vs_value() -> None:
    log.info(f"Updating '{investment_deposited_vs_value_key}' view...")
    view_content = __load_investment_deposited_vs_value()
    __store_view(investment_deposited_vs_value_key, view_content)
    log.info(f"The '{investment_deposited_vs_value_key}' view was updated")


def __load_investment_deposited_vs_value_per_wallet() -> list[dict]:
    log.info("Loading investment deposited vs value by wallet...")
    query = """
    WITH wealth_streams AS (
        SELECT id, labels->>'wallet' AS wallet
        FROM streams
        WHERE type IN ('investment', 'stocks')
          AND active = true
          AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),
    deposited AS (
        SELECT
            s.id,
            s.wallet,
            COALESCE(SUM(CASE WHEN e.type LIKE '%%Bought' OR e.type LIKE '%%Sold' OR e.type LIKE '%%Matured' THEN (e.data->>'totalValue')::numeric ELSE 0 END), 0) AS deposited
        FROM wealth_streams s
        JOIN events e ON e.stream_id = s.id
        GROUP BY s.id, s.wallet
    ),
    latest_balance AS (
        SELECT DISTINCT ON (e.stream_id)
            e.stream_id,
            (e.data->>'balance')::numeric AS value
        FROM events e
        JOIN wealth_streams s ON s.id = e.stream_id
        ORDER BY e.stream_id, e.version DESC
    ),
    combined AS (
        SELECT d.wallet, d.deposited, lb.value
        FROM deposited d
        JOIN latest_balance lb ON lb.stream_id = d.id
    )
    SELECT
        wallet,
        ROUND(SUM(deposited), 2) AS total_deposited,
        ROUND(SUM(value), 2) AS total_value
    FROM combined
    GROUP BY wallet
    ORDER BY total_value DESC;
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
                        "deposited": float(row[1] or 0),
                        "value": float(row[2] or 0),
                    }
                )
    return result


def __investment_deposited_vs_value_per_wallet() -> None:
    log.info(f"Updating '{investment_deposited_vs_value_per_wallet_key}' view...")
    view_content = __load_investment_deposited_vs_value_per_wallet()
    __store_view(investment_deposited_vs_value_per_wallet_key, view_content)
    log.info(f"The '{investment_deposited_vs_value_per_wallet_key}' view was updated")


def __load_investment_deposited_vs_value_history() -> dict:
    log.info("Loading investment deposited vs value history by type...")
    query = """
    WITH wealth_streams AS (
        SELECT id, subtype
        FROM streams
        WHERE type IN ('investment', 'stocks')
          AND active = true
          AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),
    event_months AS (
        SELECT DISTINCT date_trunc('month', e.occured_at)::date AS month_start
        FROM events e
        JOIN wealth_streams s ON s.id = e.stream_id
    ),
    month_stream_deposited AS (
        SELECT
            em.month_start,
            s.id AS stream_id,
            s.subtype,
            COALESCE(SUM(CASE WHEN e.type LIKE '%%Bought' OR e.type LIKE '%%Sold' OR e.type LIKE '%%Matured' THEN (e.data->>'totalValue')::numeric ELSE 0 END), 0) AS deposited
        FROM event_months em
        CROSS JOIN wealth_streams s
        LEFT JOIN events e ON e.stream_id = s.id
            AND e.occured_at <= (em.month_start + interval '1 month - 1 day')
        GROUP BY em.month_start, s.id, s.subtype
    ),
    month_stream_value AS (
        SELECT
            em.month_start,
            s.id AS stream_id,
            COALESCE((
                SELECT (ev.data->>'balance')::numeric
                FROM events ev
                WHERE ev.stream_id = s.id
                  AND ev.occured_at <= (em.month_start + interval '1 month - 1 day')
                ORDER BY ev.version DESC
                LIMIT 1
            ), 0) AS value
        FROM event_months em
        CROSS JOIN wealth_streams s
    )
    SELECT
        d.month_start,
        d.subtype,
        ROUND(SUM(d.deposited), 2) AS deposited,
        ROUND(SUM(v.value), 2) AS value
    FROM month_stream_deposited d
    JOIN month_stream_value v ON v.stream_id = d.stream_id AND v.month_start = d.month_start
    GROUP BY d.month_start, d.subtype
    ORDER BY d.month_start, d.subtype;
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    all_months = sorted(set(r[0] for r in rows))
    all_subtypes = sorted(set(r[1] for r in rows))
    sparse = {(r[0], r[1]): (float(r[2] or 0), float(r[3] or 0)) for r in rows}

    dates = [m.strftime("%Y-%m") for m in all_months]
    types: dict = {}

    for subtype in all_subtypes:
        dep_list: list = []
        val_list: list = []
        prev_dep = 0.0
        prev_val = 0.0
        for m in all_months:
            dep, val = sparse.get((m, subtype), (prev_dep, prev_val))
            dep_list.append(dep)
            val_list.append(val)
            prev_dep = dep
            prev_val = val
        key = subtype.replace("_", " ").title()
        types[key] = {"deposited": dep_list, "value": val_list}

    if dates and types:
        type_keys = list(types.keys())
        total_dep = [
            sum(types[k]["deposited"][i] for k in type_keys) for i in range(len(dates))
        ]
        total_val = [
            sum(types[k]["value"][i] for k in type_keys) for i in range(len(dates))
        ]
        types["total"] = {"deposited": total_dep, "value": total_val}

    return {"dates": dates, "types": types}


def __investment_deposited_vs_value_history() -> None:
    log.info(f"Updating '{investment_deposited_vs_value_history_key}' view...")
    view_content = __load_investment_deposited_vs_value_history()
    __store_view(investment_deposited_vs_value_history_key, view_content)
    log.info(f"The '{investment_deposited_vs_value_history_key}' view was updated")


def __load_investment_deposited_vs_value_history_per_wallet() -> dict:
    log.info("Loading investment deposited vs value history by wallet...")
    query = """
    WITH wealth_streams AS (
        SELECT id, labels->>'wallet' AS wallet
        FROM streams
        WHERE type IN ('investment', 'stocks')
          AND active = true
          AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),
    event_months AS (
        SELECT DISTINCT date_trunc('month', e.occured_at)::date AS month_start
        FROM events e
        JOIN wealth_streams s ON s.id = e.stream_id
    ),
    month_stream_deposited AS (
        SELECT
            em.month_start,
            s.id AS stream_id,
            s.wallet,
            COALESCE(SUM(CASE WHEN e.type LIKE '%%Bought' OR e.type LIKE '%%Sold' OR e.type LIKE '%%Matured' THEN (e.data->>'totalValue')::numeric ELSE 0 END), 0) AS deposited
        FROM event_months em
        CROSS JOIN wealth_streams s
        LEFT JOIN events e ON e.stream_id = s.id
            AND e.occured_at <= (em.month_start + interval '1 month - 1 day')
        GROUP BY em.month_start, s.id, s.wallet
    ),
    month_stream_value AS (
        SELECT
            em.month_start,
            s.id AS stream_id,
            COALESCE((
                SELECT (ev.data->>'balance')::numeric
                FROM events ev
                WHERE ev.stream_id = s.id
                  AND ev.occured_at <= (em.month_start + interval '1 month - 1 day')
                ORDER BY ev.version DESC
                LIMIT 1
            ), 0) AS value
        FROM event_months em
        CROSS JOIN wealth_streams s
    )
    SELECT
        d.month_start,
        d.wallet,
        ROUND(SUM(d.deposited), 2) AS deposited,
        ROUND(SUM(v.value), 2) AS value
    FROM month_stream_deposited d
    JOIN month_stream_value v ON v.stream_id = d.stream_id AND v.month_start = d.month_start
    GROUP BY d.month_start, d.wallet
    ORDER BY d.month_start, d.wallet;
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    all_months = sorted(set(r[0] for r in rows))
    all_wallets = sorted(set(r[1] for r in rows if r[1] is not None))
    sparse = {(r[0], r[1]): (float(r[2] or 0), float(r[3] or 0)) for r in rows}

    dates = [m.strftime("%Y-%m") for m in all_months]
    wallets: dict = {}

    for wallet in all_wallets:
        dep_list: list = []
        val_list: list = []
        prev_dep = 0.0
        prev_val = 0.0
        for m in all_months:
            dep, val = sparse.get((m, wallet), (prev_dep, prev_val))
            dep_list.append(dep)
            val_list.append(val)
            prev_dep = dep
            prev_val = val
        wallets[wallet] = {"deposited": dep_list, "value": val_list}

    if dates and wallets:
        wallet_keys = list(wallets.keys())
        total_dep = [
            sum(wallets[k]["deposited"][i] for k in wallet_keys)
            for i in range(len(dates))
        ]
        total_val = [
            sum(wallets[k]["value"][i] for k in wallet_keys) for i in range(len(dates))
        ]
        wallets["total"] = {"deposited": total_dep, "value": total_val}

    return {"dates": dates, "wallets": wallets}


def __investment_deposited_vs_value_history_per_wallet() -> None:
    log.info(
        f"Updating '{investment_deposited_vs_value_history_per_wallet_key}' view..."
    )
    view_content = __load_investment_deposited_vs_value_history_per_wallet()
    __store_view(investment_deposited_vs_value_history_per_wallet_key, view_content)
    log.info(
        f"The '{investment_deposited_vs_value_history_per_wallet_key}' view was updated"
    )


def __load_investment_deposited_vs_value_history_by_type_per_wallet() -> dict:
    log.info("Loading investment deposited vs value history by type per wallet...")
    query = """
    WITH wealth_streams AS (
        SELECT id, subtype, labels->>'wallet' AS wallet
        FROM streams
        WHERE type IN ('investment', 'stocks')
          AND active = true
          AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
    ),
    event_months AS (
        SELECT DISTINCT date_trunc('month', e.occured_at)::date AS month_start
        FROM events e
        JOIN wealth_streams s ON s.id = e.stream_id
    ),
    month_stream_deposited AS (
        SELECT
            em.month_start,
            s.id AS stream_id,
            s.subtype,
            s.wallet,
            COALESCE(SUM(CASE WHEN e.type LIKE '%%Bought' OR e.type LIKE '%%Sold' OR e.type LIKE '%%Matured' THEN (e.data->>'totalValue')::numeric ELSE 0 END), 0) AS deposited
        FROM event_months em
        CROSS JOIN wealth_streams s
        LEFT JOIN events e ON e.stream_id = s.id
            AND e.occured_at <= (em.month_start + interval '1 month - 1 day')
        GROUP BY em.month_start, s.id, s.subtype, s.wallet
    ),
    month_stream_value AS (
        SELECT
            em.month_start,
            s.id AS stream_id,
            COALESCE((
                SELECT (ev.data->>'balance')::numeric
                FROM events ev
                WHERE ev.stream_id = s.id
                  AND ev.occured_at <= (em.month_start + interval '1 month - 1 day')
                ORDER BY ev.version DESC
                LIMIT 1
            ), 0) AS value
        FROM event_months em
        CROSS JOIN wealth_streams s
    )
    SELECT
        d.month_start,
        d.wallet,
        d.subtype,
        ROUND(SUM(d.deposited), 2) AS deposited,
        ROUND(SUM(v.value), 2) AS value
    FROM month_stream_deposited d
    JOIN month_stream_value v ON v.stream_id = d.stream_id AND v.month_start = d.month_start
    GROUP BY d.month_start, d.wallet, d.subtype
    ORDER BY d.month_start, d.wallet, d.subtype;
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    # rows: (month_start, wallet, subtype, deposited, value)
    all_months = sorted(set(r[0] for r in rows))
    all_wallets = sorted(set(r[1] for r in rows if r[1] is not None))
    dates = [m.strftime("%Y-%m") for m in all_months]

    result: dict = {}
    for wallet in all_wallets:
        wallet_rows = [(r[0], r[2], r[3], r[4]) for r in rows if r[1] == wallet]
        subtypes = sorted(set(r[1] for r in wallet_rows))
        sparse = {(r[0], r[1]): (float(r[2] or 0), float(r[3] or 0)) for r in wallet_rows}

        types: dict = {}
        for subtype in subtypes:
            dep_list: list = []
            val_list: list = []
            prev_dep = 0.0
            prev_val = 0.0
            for m in all_months:
                dep, val = sparse.get((m, subtype), (prev_dep, prev_val))
                dep_list.append(dep)
                val_list.append(val)
                prev_dep = dep
                prev_val = val
            key = subtype.replace("_", " ").title()
            types[key] = {"deposited": dep_list, "value": val_list}

        if types:
            type_keys = list(types.keys())
            total_dep = [sum(types[k]["deposited"][i] for k in type_keys) for i in range(len(dates))]
            total_val = [sum(types[k]["value"][i] for k in type_keys) for i in range(len(dates))]
            types["total"] = {"deposited": total_dep, "value": total_val}

        result[wallet] = types

    return {"dates": dates, "wallets": result}


def __investment_deposited_vs_value_history_by_type_per_wallet() -> None:
    log.info(f"Updating '{investment_deposited_vs_value_history_by_type_per_wallet_key}' view...")
    view_content = __load_investment_deposited_vs_value_history_by_type_per_wallet()
    __store_view(investment_deposited_vs_value_history_by_type_per_wallet_key, view_content)
    log.info(f"The '{investment_deposited_vs_value_history_by_type_per_wallet_key}' view was updated")


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def __store_view(view_name: str, view_content):
    json_string = json.dumps(view_content, cls=JSONEncoder)

    insert_statement = """
    INSERT INTO
        views (name, content)
    VALUES
        (%s, %s::jsonb)
    ON CONFLICT
        (name)
    DO UPDATE
        SET content = %s::jsonb, updated_at = now();
    """
    db.execute(insert_statement, (view_name, json_string, json_string))
