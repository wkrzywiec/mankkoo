# todo add mocks/stubs
def test_main_indicators(test_client):
    # GIVEN

    # WHEN
    response = test_client.get('/api/main/indicators')

    # THEN
    assert response.status_code == 200
    res_body = response.get_json()

    assert res_body['savings'] >= 0
    assert 'lastMonthProfit' in res_body.keys()
    assert res_body['debt'] is None
    assert res_body['investments'] is None


def test_savings_distribution(test_client):
    # GIVEN

    # WHEN
    response = test_client.get('/api/main/savings-distribution')

    # THEN
    assert response.status_code == 200
    res_body = response.get_json()

    assert len(res_body) > 0
    assert 'type' in res_body[0].keys()
    assert 'percentage' in res_body[0].keys()
    assert 'total' in res_body[0].keys()


def test_total_history(test_client):
    # GIVEN

    # WHEN
    response = test_client.get('/api/main/total-history')

    # THEN
    assert response.status_code == 200
    res_body = response.get_json()

    assert 'date' in res_body.keys()
    assert 'total' in res_body.keys()


def test_monthly_profits(test_client):
    # GIVEN

    # WHEN
    response = test_client.get('/api/main/monthly-profits')

    # THEN
    assert response.status_code == 200
    res_body = response.get_json()

    assert 'date' in res_body.keys()
    assert 'total' in res_body.keys()
