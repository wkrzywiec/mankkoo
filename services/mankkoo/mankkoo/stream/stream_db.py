from apiflask import Schema
from apiflask.fields import String, Integer, Mapping

import mankkoo.database as db
from mankkoo.base_logger import log

class Stream(Schema):
    id = String()
    type = String()
    name = String()

def load_streams(active: bool, type: str) -> list[Stream]:
    log.info(f"Loading streams... Params: active='{active}', type='{type}'")
    conditions = []

    if active is not None:
        conditions.append(f"CAST (metadata->>'active' AS boolean) = {active}")
    
    if type is not None: 
        conditions.append(f"type = '{type}'")

    where_clause = ""

    if len(conditions) > 0:
        and_conditions = " AND ".join(conditions)
        where_clause = f"WHERE {and_conditions}"
        
    query = f"""
    SELECT
        id, type,
        CASE 
           WHEN type = 'account' THEN CONCAT(metadata->>'bankName', ' - ', metadata->>'alias')
           WHEN type = 'investment' THEN metadata->>'investmentName'
           WHEN type = 'retirement' THEN metadata->>'alias'
           WHEN type = 'stocks' AND metadata->>'type' = 'ETF' THEN metadata->>'etfName'
           ELSE 'Unknown'
        END AS name
    FROM
        streams
    {where_clause}
    ;
    """
    
    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                stream = Stream()
                stream.id = row[0]
                stream.type = row[1]
                stream.name = row[2]
                
                result.append(stream)
    return result



class StreamDetails(Schema):
    id = String()
    type = String()
    version = Integer()
    metadata = Mapping()

def load_stream_by_id(stream_id) -> StreamDetails:
    log.info(f"Loading stream '{stream_id}'...")
    query = f"""
    SELECT
        id, type, version, metadata
    FROM streams
    WHERE id = '{stream_id}'
    ;
    """

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
            if result is None:
                return None

    try:
        stream = Stream()
        stream.id = result[0]
        stream.type = result[1]
        stream.version = result[2]
        stream.metadata = result[3]
        
        log.info(f"Found stream by id {stream_id}")
        return stream
    except Exception:
        raise ValueError(f"Failed to load stream definition. Mapping internal error. Check the logs")
