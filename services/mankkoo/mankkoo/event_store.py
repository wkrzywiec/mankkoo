from datetime import datetime
import json
import uuid
from uuid import UUID

import mankkoo.database as db
from mankkoo.base_logger import log

log.basicConfig(level=log.DEBUG)


class Stream:
    def __init__(self, id: UUID, type: str, version: int, metadata: dict):
        self.id = id
        self.type = type
        self.version = version
        self.metadata = metadata

    def __str__(self):
        return f"Stream(id={self.id}, type={self.type}, version={self.version}, metadata={self.metadata})"

    def __eq__(self, other):
        if not isinstance(other, Stream):
            return NotImplemented

        return self.id == other.id and self.type == other.type and self.version == other.version and self.metadata == other.metadata

    def __hash__(self):
        return hash(self.id, self.type, self.version, self.metadata)


class Event:
    def __init__(self, stream_type: str, stream_id: UUID, event_type: str, data: dict, occured_at: datetime, version=1, event_id: UUID = None):
        if event_id is None:
            event_id = uuid.uuid4()
        self.id = event_id
        self.stream_type = stream_type
        self.stream_id = stream_id
        self.event_type = event_type
        self.version = version
        self.data = data
        self.occured_at = occured_at

    def __str__(self):
        return f"Event(id={self.id}, stream_type={self.stream_type}, stream_id={self.stream_id}, event_type={self.event_type}, data={self.data}, occured_at={self.occured_at}, version={self.version})"

    def __eq__(self, other):
        if not isinstance(other, Event):
            return NotImplemented

        return self.id == other.id and self.stream_type == other.stream_type and self.stream_id == other.stream_id and self.event_type == other.event_type and self.version == other.version and self.occured_at == other.occured_at and self.data == other.data

    def __hash__(self):
        return hash(self.id, self.stream_type, self.stream_id, self.event_type, self.version, self.occured_at, self.data)


def store(events: list[Event]):
    log.info(f"Storing {len(events)} event(s)...")
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            for event in events:
                log.info(f"Storing {event}...")
                cur.execute(
                    "SELECT append_event(%s::uuid, %s::jsonb, %s::text, %s::uuid, %s::text, %s, %s::bigint);",
                    (str(event.id), json.dumps(event.data), event.event_type, str(event.stream_id), event.stream_type, event.occured_at, event.version)
                )
            conn.commit()
    log.info("All events have been stored")


def load(stream_id: UUID) -> list[Event]:
    log.info(f"Loading events for a stream {stream_id}...")
    result = []

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, stream_id, type, data, version, occured_at from events WHERE stream_id = '{str(stream_id)}' ORDER BY version")
            rows = cur.fetchall()

            for row in rows:
                print(row)
                result.append(
                    Event(event_id=uuid.UUID(row[0]), stream_id=uuid.UUID(row[1]), event_type=row[2], data=row[3], version=row[4], occured_at=row[5], stream_type="account")
                )

    return result


def get_stream_by_metadata(key: str, value) -> Stream | None:
    log.info(f"Loading stream by its matadata property key '{key}' and value '{value}'...")
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, type, version, metadata from streams WHERE metadata ->> '{key}' = '{value}'")
            result = cur.fetchone()
            if result is None:
                return None
            else:
                (id, type, version, metadata, ) = result
    return Stream(uuid.UUID(id), type, version, metadata)


def get_stream_metadata(stream_id: UUID) -> dict:
    log.info(f"Loading stream's '{stream_id}' metadata...")
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT metadata from streams WHERE id = '" + str(stream_id) + "'")
            (metadata, ) = cur.fetchone()
    return metadata


def update_stream_metadata(stream_id: UUID, metadata: dict):
    log.info(f"Updating stream '{stream_id}' with metdata '{metadata}'...")
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE streams SET metadata = %s::jsonb WHERE id = %s::uuid;",
                (json.dumps(metadata), str(stream_id))
            )
            conn.commit()


def get_all_streams() -> dict:
    # get map of accountNumber: stream_id (uuid)
    result = {}

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT metadata-> 'accountNumber' AS account_number, id FROM streams;")
            rows = cur.fetchall()

            for row in rows:
                result[row[0]] = uuid.UUID(row[1])

    return result
