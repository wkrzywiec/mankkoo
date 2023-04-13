from accounting.app import app

def test_main_indicators():
    #GIVEN

    #WHEN
    response = app.test_client().get('/api/main/indicators')

    #THEN
    assert response.status_code == 200
    res_body = response.get_json()

    assert res_body['savings'] >= 0
    assert res_body['lasyMonthProfit'] != 0
    assert res_body['debt'] == 0
    assert res_body['investments'] == 0