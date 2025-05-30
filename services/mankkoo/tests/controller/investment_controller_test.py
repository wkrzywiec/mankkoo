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
