from datetime import date
from decimal import Decimal
import json

import mankkoo.database as db
import mankkoo.total as total

from mankkoo.base_logger import log

main_indicators_key = 'main-indicators'
current_savings_distribution_key = 'current-savings-distribution'
total_history_per_day_key = 'total-history-per-day'


def load_view(view_name):
    log.info(f"Loading '{view_name}' view...")
    query = f"""
    SELECT
        content
    FROM
        views
    WHERE name = '{view_name}';
    """

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            (view, ) = cur.fetchone()

    return view


def update_views(oldest_occured_event_date: date):
    log.info(f'Updating views... (input: {oldest_occured_event_date})')
    __main_indicators()
    __current_total_savings_distribution()
    __total_history_per_day(oldest_occured_event_date)


def __main_indicators():
    log.info(f"Updating '{main_indicators_key}' view...")
    current_total_savings = total.current_total_savings()

    view_content = {
        'savings': current_total_savings,
        'debt': None,
        'lastMonthProfit': 0,
        'investments': None
    }
    __store_view(main_indicators_key, view_content)
    log.info(f"The '{main_indicators_key}' view was updated")


def __current_total_savings_distribution():
    log.info(f"Updating '{current_savings_distribution_key}' view...")
    view_content = total.current_total_savings_distribution()

    __store_view(current_savings_distribution_key, view_content)
    log.info(f"The '{current_savings_distribution_key}' view was updated")


def __total_history_per_day(oldest_occured_event_date: date):
    log.info(f"Updating '{total_history_per_day_key}' view...")
    view_content = total.total_history_per_day(oldest_occured_event_date)

    __store_view(total_history_per_day_key, view_content)
    log.info(f"The '{total_history_per_day_key}' view was updated")


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def __store_view(view_name: str, view_content: dict):
    json_string = json.dumps(view_content, cls=JSONEncoder)

    insert_statement = f"""
    INSERT INTO
        views (name, content)
    VALUES
        ('{view_name}', '{json_string}'::jsonb)
    ON CONFLICT
        (name)
    DO UPDATE
        SET content = '{json_string}'::jsonb, updated_at = now();
    """
    db.execute(insert_statement)
