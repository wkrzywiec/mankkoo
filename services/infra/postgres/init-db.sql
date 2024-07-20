CREATE TABLE IF NOT EXISTS events
(
    id              UUID                      NOT NULL    PRIMARY KEY,
    stream_id       UUID                      NOT NULL,
    type            TEXT                      NOT NULL,
    data            JSONB                     NOT NULL,
    version         BIGINT                    NOT NULL,
    occured_at      timestamp with time zone  NOT NULL,
    added_at        timestamp with time zone  NOT NULL    default (now()),
    
    CONSTRAINT events_stream_and_version UNIQUE(stream_id, version)
);

CREATE OR REPLACE FUNCTION append_event
(
    id uuid,
    data jsonb,
    type text,
    stream_id uuid,
    stream_type text,
    occured_at timestamp with time zone,
    expected_stream_version bigint default null
) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
    DECLARE
        stream_version int;
    BEGIN
        
        -- get stream version
        SELECT
            MAX(version) INTO stream_version
        FROM events as s
        WHERE
            s.id = stream_id FOR UPDATE;

        -- if stream doesn't exist - create new one with version 0
        IF stream_version IS NULL THEN
            stream_version := 0;
        END IF;

        -- check optimistic concurrency
        IF expected_stream_version IS NOT NULL AND stream_version != expected_stream_version THEN
            RETURN FALSE;
        END IF;

        -- increment event_version
        stream_version := stream_version + 1;

        -- append event
        INSERT INTO events
            (id, data, stream_id, type, version, occured_at)
        VALUES
            (id, data::jsonb, stream_id, type, stream_version, occured_at);

        RETURN TRUE;
    END;
    $$;