from datetime import datetime
import json
import uuid
from uuid import UUID


import mankkoo.database as db
from mankkoo.base_logger import log

log.basicConfig(level=log.DEBUG)

class Event:
    def __init__(self, stream_type: str, stream_id: UUID, event_type: str, data: dict, occured_at: datetime, version=1, event_id=None):
        if event_id == None:
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

def store(events: list[Event]) -> bool:
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

def update_stream_metadata(stream_id: UUID, metadata: dict):
    pass
