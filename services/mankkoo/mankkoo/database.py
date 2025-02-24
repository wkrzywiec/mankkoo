import os
import psycopg2

from mankkoo.base_logger import log

log.basicConfig(level=log.DEBUG)

account_columns = ['Account', 'Date', 'Title', 'Details', 'Category', 'Comment', 'Operation', 'Currency', 'Balance']
invest_columns = ['Active', 'Category', 'Bank', 'Investment', 'Start Date', 'End Date', 'Start Amount', 'End amount', 'Currency', 'Details', 'Comment']
stock_columns = ['Broker', 'Date', 'Title', 'Operation', 'Total Value', 'Units', 'Currency', 'Details', 'Url', 'Comment']
total_columns = ['Date', 'Total']
total_monthly_columns = ['Date', 'Income', 'Spending', 'Profit']


def init_db():
    log.info("Initializing database with tables and functions...")
    execute("""
        CREATE TABLE IF NOT EXISTS streams
        (
            id              UUID                      NOT NULL    PRIMARY KEY,
            type            TEXT                      NOT NULL,
            version         BIGINT                    NOT NULL,
            metadata        JSONB
        );

        CREATE TABLE IF NOT EXISTS events
        (
            id              UUID                      NOT NULL    PRIMARY KEY,
            stream_id       UUID                      NOT NULL,
            type            TEXT                      NOT NULL,
            data            JSONB                     NOT NULL,
            version         BIGINT                    NOT NULL,
            occured_at      timestamp with time zone  NOT NULL,
            added_at        timestamp with time zone  NOT NULL    default (now()),

            FOREIGN KEY(stream_id) REFERENCES streams(id),
            CONSTRAINT events_stream_and_version UNIQUE(stream_id, version)
        );

        CREATE TABLE IF NOT EXISTS views
        (
            name            TEXT                      NOT NULL    PRIMARY KEY,
            content         JSONB,
            updated_at      timestamp with time zone  NOT NULL    default (now())
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
                error_message text;
            BEGIN

                -- get stream version
                SELECT
                    version INTO stream_version
                FROM streams as s
                WHERE
                    s.id = stream_id FOR UPDATE;

                -- if stream doesn't exist - create new one with version 0
                IF stream_version IS NULL THEN
                    stream_version := 0;

                    INSERT INTO streams
                        (id, type, version)
                    VALUES
                        (stream_id, stream_type, stream_version);
                END IF;

                -- increment event_version
                stream_version := stream_version + 1;

                -- check optimistic concurrency
                IF expected_stream_version IS NOT NULL AND stream_version != expected_stream_version THEN
                    RAISE EXCEPTION 'Expecting "%', stream_version || '" as next stream version but "' || expected_stream_version || '" was provided';
                END IF;

                -- append event
                INSERT INTO events
                    (id, data, stream_id, type, version, occured_at)
                VALUES
                    (id, data::jsonb, stream_id, type, stream_version, occured_at);


                -- update stream version
                UPDATE streams as s
                    SET version = stream_version
                WHERE
                    s.id = stream_id;

                RETURN TRUE;
            END;
            $$;

        CREATE OR REPLACE FUNCTION notification_trigger() RETURNS TRIGGER AS
            $$
            DECLARE
                oldest_occured_date text;
            BEGIN

                SELECT min(occured_at)::date::text
                INTO oldest_occured_date
                FROM events WHERE added_at >= NOW() - interval '20 days';

                PERFORM pg_notify('events_added', oldest_occured_date);
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

        CREATE OR REPLACE TRIGGER capture_event_added_trigger AFTER INSERT ON events
        FOR EACH STATEMENT EXECUTE FUNCTION notification_trigger();
        """)

    log.info("Database initialized")


def execute(sql: str):
    # log.info(f"Executing sql: {sql}")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()


def get_connection():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "postgres")
    username = os.getenv("DB_USERNAME", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    log.info(f'Getting connection to db: postgresql://{host}:{port}/{database}?user={username}&password={password}...')

    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=username,
        password=password
    )
    return conn
