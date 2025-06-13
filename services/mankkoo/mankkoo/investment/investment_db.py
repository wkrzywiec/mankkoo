import re

import mankkoo.database as db
from mankkoo.base_logger import log


def load_wallets() -> list[str]:
    log.info("Loading wallets...")
    query = """
    SELECT DISTINCT labels->>'wallet' AS wallet
    FROM streams
    WHERE labels ? 'wallet' AND labels->>'wallet' IS NOT NULL AND labels->>'wallet' != ''
    ORDER BY wallet;
    """
    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                result.append(row[0])
    return result


def load_investments(active: bool, wallet: str) -> list[dict]:
    conditions = []
    # Only allow investment, stocks, or account (savings)
    conditions.append(
        "(s.type IN ('investment', 'stocks') OR (s.type = 'account' AND s.metadata->>'accountType' = 'savings'))"
    )

    if active is not None:
        if active:
            conditions.append(
                f"(CAST (s.metadata->>'active' AS boolean) = {active} OR NOT (s.metadata ? 'active'))"
            )
        else:
            conditions.append(f"CAST (s.metadata->>'active' AS boolean) = {active}")
    if wallet:
        conditions.append(f"s.labels->>'wallet' = '{wallet}'")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
    WITH latest_events AS (
        SELECT DISTINCT ON (e.stream_id) e.stream_id, e.data, e.version
        FROM events e
        ORDER BY e.stream_id, e.version DESC
    )
    SELECT s.id,
        CASE
            WHEN s.type = 'investment' THEN s.metadata->>'investmentName'
            WHEN s.type = 'stocks' THEN s.metadata->>'etfName'
            WHEN s.type = 'account' THEN s.metadata->>'accountName'
            ELSE NULL
        END AS name,
        CASE
            WHEN s.type = 'investment' THEN 'investment'
            WHEN s.type = 'stocks' THEN 'stocks'
            WHEN s.type = 'account' THEN 'account'
            ELSE s.type
        END AS investment_type,
        CASE
            WHEN s.type = 'investment' THEN s.metadata->>'category'
            WHEN s.type = 'stocks' THEN s.metadata->>'type'
            WHEN s.type = 'account' THEN s.metadata->>'accountType'
            ELSE NULL
        END AS subtype,
        COALESCE((le.data->>'balance')::numeric, 0) AS balance
    FROM streams s
    LEFT JOIN latest_events le ON le.stream_id = s.id AND le.version = s.version
    {where_clause}
    ORDER BY balance DESC;
    """

    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            for row in cur.fetchall():
                result.append(
                    {
                        "id": str(row[0]),
                        "name": row[1],
                        "investmentType": row[2],
                        "subtype": row[3],
                        "balance": float(row[4]) if row[4] is not None else 0.0,
                    }
                )
    return result


def load_investment_transactions(investment_id: str) -> list[dict]:
    query = f"""
        SELECT
            occured_at::date AS occured_at,
            e.type AS event_type,
            (e.data->>'units')::numeric AS units_count,
            CASE
                WHEN s.type = 'investment' THEN (e.data->>'pricePerUnit')::numeric
                WHEN s.type = 'account' THEN (e.data->>'amount')::numeric
                ELSE (e.data->>'averagePrice')::numeric
            END AS price_per_unit,
            CASE
                WHEN s.type = 'account' THEN (e.data->>'amount')::numeric
                ELSE (e.data->>'totalValue')::numeric
            END AS total_value,
            (e.data->>'balance')::numeric AS balance,
            e.data->>'comment' AS comment
        FROM events e
        JOIN streams s ON e.stream_id = s.id
        WHERE e.stream_id = '{investment_id}'
        ORDER BY e.version DESC;
    """

    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            for row in cur.fetchall():
                result.append(
                    {
                        "occuredAt": row[0],
                        "eventType": __camel_to_words(row[1]) if row[1] else None,
                        "unitsCount": float(row[2]) if row[2] is not None else None,
                        "pricePerUnit": float(row[3]) if row[3] is not None else None,
                        "totalValue": float(row[4]) if row[4] is not None else None,
                        "balance": float(row[5]) if row[5] is not None else None,
                        "comment": row[6] if row[6] is not None else None,
                    }
                )
    return result


def __camel_to_words(name):
    # If there are multiple consecutive capitals, only split before the last capital
    # e.g. ETFBought -> ETF Bought, USDDeposit -> USD Deposit
    match = re.match(r"([A-Z]+)([A-Z][a-z].*)", name)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    # Otherwise, split before each capital except the first
    return re.sub(r"(?<!^)(?=[A-Z])", " ", name)
