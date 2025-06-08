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


def load_all_investments(active: bool, wallet: str = None) -> list[dict]:
    query = """
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
            WHEN s.type = 'stocks' THEN s.metadata->>'broker'
            WHEN s.type = 'account' THEN s.metadata->>'accountType'
            ELSE NULL
        END AS subtype,
        COALESCE((le.data->>'balance')::numeric, 0) AS balance
    FROM streams s
    LEFT JOIN latest_events le ON le.stream_id = s.id AND le.version = s.version
    WHERE (
        s.type IN ('investment', 'stocks')
        OR (s.type = 'account' AND s.metadata->>'accountType' = 'savings')
    )
    """
    params = []
    if active is not None:
        if active:
            query += f" AND (CAST (metadata->>'active' AS boolean) = {active} OR NOT (metadata ? 'active'))"
        else:
            query += f" AND CAST (metadata->>'active' AS boolean) = {active}"
    if wallet:
        query += " AND s.labels->>'wallet' = %s"
        params.append(wallet)

    query += " ORDER BY balance DESC;"
    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            for row in cur.fetchall():
                result.append({
                    'id': str(row[0]),
                    'name': row[1],
                    'investmentType': row[2],
                    'subtype': row[3],
                    'balance': float(row[4]) if row[4] is not None else 0.0
                })
    return result
