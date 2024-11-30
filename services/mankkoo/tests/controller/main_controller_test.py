import json

import mankkoo.views as views
import mankkoo.database as db


def test_main_indicators(test_client):
    # GIVEN
    view = {
        "debt": None,
        "savings": 1235.78,
        "investments": None,
        "lastMonthProfit": -4567.89
    }
    insert_view(views.main_indicators_key, view)

    # WHEN
    response = test_client.get('/api/main/indicators')

    # THEN
    assert response.status_code == 200
    res_body = response.get_json()

    assert res_body == view


def test_savings_distribution(test_client):
    # GIVEN
    view = [
        {
            "type": "checking",
            "total": 3467.07,
            "percentage": 0.3467
        },
        {
            "type": "savings",
            "total": 9740.01,
            "percentage": 0.2974
        },
        {
            "type": "cash",
            "total": 0,
            "percentage": 0
        },
        {
            "type": "stocks",
            "total": 2590.3,
            "percentage": 0.259
        },
        {
            "type": "retirement",
            "total": 969,
            "percentage": 0.0969
        }
    ]
    insert_view(views.current_savings_distribution_key, view)

    # WHEN
    response = test_client.get('/api/main/savings-distribution')

    # THEN
    assert response.status_code == 200
    res_body = response.get_json()
    assert view == res_body


def test_total_history(test_client):
    # GIVEN
    view = {
        "date": ["2021-01-01", "2021-01-02", "2021-01-03"],
        "total": [1123.34, 1123.34, 789.87]
    }
    insert_view(views.total_history_per_day_key, view)

    # WHEN
    response = test_client.get('/api/main/total-history')

    # THEN
    assert response.status_code == 200
    res_body = response.get_json()
    assert view == res_body


def insert_view(name: str, content: dict | list):
    db.execute("TRUNCATE views;") # not sure why this is needed since before each test db is cleaned up 
    db.execute(f"INSERT INTO views (name, content) VALUES ('{name}', '{json.dumps(content)}'::jsonb);")
