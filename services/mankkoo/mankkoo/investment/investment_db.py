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


def load_all_investments(active: str = None, wallet: str = None) -> list[dict]:
    query = """
    SELECT id,
        CASE
            WHEN type = 'investment' THEN metadata->>'investmentName'
            WHEN type = 'stocks' THEN metadata->>'etfName'
            WHEN type = 'account' THEN metadata->>'accountName'
            ELSE NULL
        END AS name,
        CASE
            WHEN type = 'investment' THEN 'investment'
            WHEN type = 'stocks' THEN 'stocks'
            WHEN type = 'account' THEN 'account'
            ELSE type
        END AS investment_type,
        CASE
            WHEN type = 'investment' THEN metadata->>'category'
            WHEN type = 'stocks' THEN metadata->>'broker'
            WHEN type = 'account' THEN metadata->>'accountType'
            ELSE NULL
        END AS subtype,
        COALESCE((metadata->>'balance')::numeric, 0) AS balance
    FROM streams
    WHERE (
        type IN ('investment', 'stocks')
        OR (type = 'account' AND metadata->>'accountType' = 'savings')
    )
    """
    params = []
    if active is not None:
        if active.lower() == 'true':
            query += " AND (endDate IS NULL OR endDate > CURRENT_DATE)"
        elif active.lower() == 'false':
            query += " AND (endDate IS NOT NULL AND endDate <= CURRENT_DATE)"
    if wallet:
        query += " AND labels->>'wallet' = %s"
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
