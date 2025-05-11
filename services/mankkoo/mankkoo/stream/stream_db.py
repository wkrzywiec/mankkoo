from apiflask import Schema
from apiflask.fields import String, Integer, Mapping, Date

import mankkoo.database as db
from mankkoo.base_logger import log


class Stream(Schema):
    id = String()
    type = String()
    name = String()
    wallet = String()


def load_streams(active: bool, type: str) -> list[Stream]:
    log.info(f"Loading streams... Params: active='{active}', type='{type}'")
    conditions = []

    if active is not None:
        if active:
            conditions.append(f"(CAST (metadata->>'active' AS boolean) = {active} OR NOT (metadata ? 'active'))")
        else:
            conditions.append(f"CAST (metadata->>'active' AS boolean) = {active}")

    if type is not None:
        conditions.append(f"type = '{type}'")

    where_clause = ""

    if len(conditions) > 0:
        and_conditions = " AND ".join(conditions)
        where_clause = f"WHERE {and_conditions}"

    query = f"""
    SELECT
        id,
        CASE
           WHEN type = 'account' THEN metadata->>'accountType'
           WHEN type = 'investment' THEN metadata->>'category'
           WHEN type = 'retirement' THEN metadata->>'accountType'
           WHEN type = 'stocks' THEN metadata->>'type'
           ELSE type
        END AS type
        ,
        CASE
           WHEN type = 'account' THEN CONCAT(metadata->>'bankName', ' - ', metadata->>'alias')
           WHEN type = 'investment' THEN metadata->>'investmentName'
           WHEN type = 'retirement' THEN metadata->>'alias'
           WHEN type = 'stocks' AND metadata->>'type' = 'ETF' THEN metadata->>'etfName'
           ELSE 'Unknown'
        END AS name
        ,
        labels->>'wallet' AS wallet
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
                stream.wallet = row[3]

                result.append(stream)
    return result


class StreamsQueryResult(Schema):
    id = String()
    type = String()
    name = String()
    version = Integer()
    metadata = Mapping()
    labels = Mapping()


def load_stream_by_id(stream_id: str) -> StreamsQueryResult | None:
    log.info(f"Loading stream by id '{stream_id}'...")
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, type,
                CASE
                    WHEN type = 'account' THEN CONCAT(metadata->>'bankName', ' - ', metadata->>'alias')
                    WHEN type = 'investment' THEN metadata->>'investmentName'
                    WHEN type = 'retirement' THEN metadata->>'alias'
                    WHEN type = 'stocks' AND metadata->>'type' = 'ETF' THEN metadata->>'etfName'
                    ELSE 'Unknown'
                END AS name,
                version,
                metadata,
                labels
                FROM streams WHERE id = '{stream_id}';
                        """)
            result = cur.fetchone()
            if result is None:
                return None
            else:
                (id, type, name, version, metadata, labels) = result
                stream = StreamsQueryResult()
                stream.id = id
                stream.type = type
                stream.name = name
                stream.version = version
                stream.metadata = metadata
                stream.labels = labels
                return stream


class Event(Schema):
    type = String()
    version = Integer()
    occuredAt = Date()
    addedAt = Date()
    data = Mapping()


def load_events_for_stream(stream_id):
    log.info(f"Loading events for the '{stream_id}' stream...")

    query = f"""
    SELECT
        type, version, occured_at, added_at, data
    FROM
        events
    WHERE
        stream_id = '{stream_id}'
    ORDER BY
        version DESC
    ;
    """

    result = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                event = Event()
                event.type = row[0]
                event.version = row[1]
                event.occuredAt = row[2]
                event.addedAt = row[3]
                event.data = row[4]

                result.append(event)
    return result
