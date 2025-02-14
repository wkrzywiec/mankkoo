from apiflask import Schema
from apiflask.fields import String, Integer

import mankkoo.database as db
from mankkoo.base_logger import log

class Stream(Schema):
    id = String()
    type = String()
    name = String()

def load_streams(active: bool, type: str) -> list[Stream]:
    log.info(f"Loading stream... Params: active={active}, type={type}")
    conditions = []

    # if active is not None:
    #     conditions.append(f"metadata->>'active' = '{active}'")
    
    # if type is not None: 
    #     conditions.append(f"type = '{type}'")

    # where_clause = ""

    # if len(conditions) > 0:
    #     where_clause = f"WHERE {conditions[0]}"
    
    #     if len(conditions) > 1:
    #         and_cond = " AND ".join() 
        
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

