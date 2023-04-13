from accounting.app import app

#todo add mocks/stubs

def test_main_indicators():
    #GIVEN

    #WHEN
    response = app.test_client().get('/api/main/indicators')

    #THEN
    assert response.status_code == 200
    res_body = response.get_json()

    assert res_body['savings'] >= 0
    assert 'lasyMonthProfit' in res_body.keys()
    assert res_body['debt'] == 0
    assert res_body['investments'] == 0

def test_savings_distribution():
    #GIVEN

    #WHEN
    response = app.test_client().get('/api/main/savings-distribution')

    #THEN
    assert response.status_code == 200
    res_body = response.get_json()

    assert 'keys' in res_body.keys()
    assert 'values' in res_body.keys()
    assert 'total' in res_body.keys()