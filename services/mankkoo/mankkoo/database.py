import os
import pandas as pd
import psycopg2

import mankkoo.util.config as config
from mankkoo.base_logger import log
from mankkoo.account import account_db

log.basicConfig(level=log.DEBUG)

account_columns = ['Account', 'Date', 'Title', 'Details', 'Category', 'Comment', 'Operation', 'Currency', 'Balance']
invest_columns = ['Active', 'Category', 'Bank', 'Investment', 'Start Date', 'End Date', 'Start Amount', 'End amount', 'Currency', 'Details', 'Comment']
stock_columns = ['Broker', 'Date', 'Title', 'Operation', 'Total Value', 'Units', 'Currency', 'Details', 'Url', 'Comment']
total_columns = ['Date', 'Total']
total_monthly_columns = ['Date', 'Income', 'Spending', 'Profit']


def load_all() -> dict:
    """Load aggregated data of all financial data (accounts, investments, etc.)

    Returns:
        dict(pandas.DataFrame): a dictonary with categorized financial data
    """
    log.info("Loading mankkoo's files")

    return dict(
        account=account_db.load_all_operations_as_df(),
        investment=load_investments(),
        stock=load_stocks(),
        total=load_total(),
        total_monthly=load_total_monthly()
    )


def load_total() -> pd.DataFrame:
    log.info('Loading TOTAL file')

    result = pd.read_csv(config.mankkoo_file_path('total'), parse_dates=['Date'])
    result = result.astype({'Date': 'datetime64[ns]', 'Total': 'float'})
    result['Date'] = result['Date'].dt.date
    return result


def load_total_monthly() -> pd.DataFrame:
    log.info('Loading TOTAL MONTHLY file')

    result = pd.read_csv(config.mankkoo_file_path('total_monthly'), parse_dates=['Date'])
    result = result.astype({'Date': 'datetime64[ns]', 'Income': 'float', 'Spending': 'float', 'Profit': 'float'})
    result['Date'] = result['Date'].dt.date
    return result


def load_investments() -> pd.DataFrame:
    log.info('Loading INVESTMENT file')

    result = pd.read_csv(config.mankkoo_file_path('investment'), parse_dates=['Start Date', 'End Date'])
    result = result.astype({'Active': 'int', 'Start Amount': 'float', 'End amount': 'float', 'Start Date': 'datetime64[ns]', 'End Date': 'datetime64[ns]'})
    result.Active = result.Active.astype('bool')
    result['Start Date'] = result['Start Date'].dt.date
    result['End Date'] = result['End Date'].dt.date
    return result


def load_stocks() -> pd.DataFrame:
    log.info('Loading STOCK file')

    result = pd.read_csv(config.mankkoo_file_path('stock'), parse_dates=['Date'])
    result = result.astype({'Total Value': 'float', 'Date': 'datetime64[ns]'})
    result['Date'] = result['Date'].dt.date
    return result


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
        """)

    log.info("Database initialized")


def execute(sql: str):
    log.info(f"Executing sql: {sql}")
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
