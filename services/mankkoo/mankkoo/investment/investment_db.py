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
