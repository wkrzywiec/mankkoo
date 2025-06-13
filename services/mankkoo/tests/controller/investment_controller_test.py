import uuid

import mankkoo.event_store as es


def test_investment_wallets_endpoint__returns_wallet_list(test_client):
    # GIVEN
    wallets = ["Wallet A", "Wallet B", "Wallet C"]
    streams = []
    for wallet_label in wallets:
        stream = es.Stream(
            uuid.uuid4(),
            "investment",
            version=0,
            metadata={"active": True},
            labels={"wallet": wallet_label},
        )
        streams.append(stream)
    es.create(streams)

    # WHEN
    response = test_client.get("/api/investments/wallets")

    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    assert "wallets" in payload
    assert set(payload["wallets"]) == set(wallets)


def test_get_investments_no_query_params(test_client):
    # GIVEN
    streams = _create_investment_test_streams()
    # WHEN
    response = test_client.get("/api/investments")
    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    ids = [item["id"] for item in payload]
    # Should include all active and inactive investments, stocks, and savings accounts
    for s in streams.values():
        assert str(s.id) in ids


def test_get_investments_inactive_only(test_client):
    # GIVEN
    streams = _create_investment_test_streams()
    # WHEN
    response = test_client.get("/api/investments?active=false")
    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    ids = [item["id"] for item in payload]
    # Only inactive investment and savings
    assert str(streams["investment_inactive"].id) in ids
    assert str(streams["savings_inactive"].id) in ids
    assert str(streams["investment"].id) not in ids
    assert str(streams["savings"].id) not in ids
    assert str(streams["etf"].id) not in ids


def test_get_investments_active_and_by_wallet(test_client):
    # GIVEN
    streams = _create_investment_test_streams()
    # WHEN
    response = test_client.get("/api/investments?active=true&wallet=Wallet%20B")
    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    ids = [item["id"] for item in payload]
    # Only active investment in Wallet B
    assert str(streams["investment"].id) in ids
    assert str(streams["investment_inactive"].id) not in ids
    assert str(streams["etf"].id) not in ids
    assert str(streams["savings"].id) not in ids
    assert str(streams["savings_inactive"].id) not in ids


def _create_investment_test_streams():
    # ETF stock (active)
    etf_stream = es.Stream(
        uuid.uuid4(),
        "stocks",
        0,
        {"active": True, "type": "ETF", "broker": "Broker1", "etfName": "ETFSP500"},
        {"wallet": "Wallet A"},
    )
    # Investment (active)
    investment_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        0,
        {"active": True, "category": "bonds", "investmentName": "Bond2025"},
        {"wallet": "Wallet B"},
    )
    # Investment (inactive)
    investment_stream_inactive = es.Stream(
        uuid.uuid4(),
        "investment",
        0,
        {"active": False, "category": "bonds", "investmentName": "Bond2020"},
        {"wallet": "Wallet B"},
    )
    # Savings account (active)
    savings_stream = es.Stream(
        uuid.uuid4(),
        "account",
        0,
        {"active": True, "accountType": "savings", "accountName": "MySavings"},
        {"wallet": "Wallet C"},
    )
    # Savings account (inactive)
    savings_stream_inactive = es.Stream(
        uuid.uuid4(),
        "account",
        0,
        {"active": False, "accountType": "savings", "accountName": "OldSavings"},
        {"wallet": "Wallet C"},
    )
    es.create(
        [
            etf_stream,
            investment_stream,
            investment_stream_inactive,
            savings_stream,
            savings_stream_inactive,
        ]
    )
    return {
        "etf": etf_stream,
        "investment": investment_stream,
        "investment_inactive": investment_stream_inactive,
        "savings": savings_stream,
        "savings_inactive": savings_stream_inactive,
    }

