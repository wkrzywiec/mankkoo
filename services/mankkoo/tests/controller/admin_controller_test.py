import mankkoo.views as views


def test_all_views_are_returned(test_client):
    # WHEN
    response = test_client.get('/api/admin/views')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert 'views' in payload
    assert len(payload['views']) == 5
    assert views.main_indicators_key in payload['views']
    assert views.current_savings_distribution_key in payload['views']
    assert views.total_history_per_day_key in payload['views']
    assert views.investment_indicators_key in payload['views']
    assert views.investment_types_distribution_key in payload['views']
    assert views.investment_wallets_distribution_key in payload['views']


def test_specific_view_is_loaded(test_client):
    # GIVEN
    view_name = views.main_indicators_key

    # WHEN
    response = test_client.get(f'/api/admin/views/{view_name}')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert payload is not None
    assert isinstance(payload, dict)
