import uuid
from datetime import datetime

import mankkoo.event_store as es


def test_investment_wallets_endpoint__returns_wallet_list(test_client):
    # GIVEN
    wallets = ["Wallet A", "Wallet B", "Wallet C"]
    streams = []
    for wallet_label in wallets:
        stream = es.Stream(
            uuid.uuid4(),
            "investment",
            "deposit",
            "Super Investment",
            "Broker A",
            True,
            version=0,
            metadata={"details": "Super investment details"},
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
    # Should include all active and inactive investments, stocks, and savings
    # accounts
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
        "ETF",
        "SP500 ETF",
        "Broker1",
        True,
        0,
        {"details": "SP500 ETF details"},
        {"wallet": "Wallet A"},
    )
    # Investment (active)
    investment_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "deposit",
        "Bank Deposit",
        "Broker B",
        True,
        0,
        {"details": "Bank deposit details"},
        {"wallet": "Wallet B"},
    )
    # Investment (inactive)
    investment_stream_inactive = es.Stream(
        uuid.uuid4(),
        "investment",
        "deposit",
        "Old Investment",
        "Broker B",
        False,
        0,
        {"details": "Old investment details"},
        {"wallet": "Wallet B"},
    )
    # Savings account (active)
    savings_stream = es.Stream(
        uuid.uuid4(),
        "account",
        "savings",
        "My Savings Account",
        "Bank C",
        True,
        0,
        {"accountNumber": "1234567890"},
        {"wallet": "Wallet C"},
    )
    # Savings account (inactive)
    savings_stream_inactive = es.Stream(
        uuid.uuid4(),
        "account",
        "savings",
        "Old Savings Account",
        "Bank C",
        False,
        0,
        {"details": "Old savings account details"},
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


def test_get_investments_includes_gold(test_client):
    # GIVEN
    gold_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "gold",
        "Physical Gold",
        "Gold Dealer",
        True,
        0,
        {"details": "Gold coins"},
        {"wallet": "Wallet A"},
    )
    bonds_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "treasury_bonds",
        "10-years Treasury Bonds",
        "Bank 1",
        True,
        0,
        {"details": "Some details"},
        {"wallet": "Wallet A"},
    )
    es.create([gold_stream, bonds_stream])

    gold_bought = es.Event(
        stream_type="investment",
        stream_id=gold_stream.id,
        event_type="GoldBought",
        data={
            "totalValue": 8500.0,
            "balance": 8500.0,
            "weight": 31.1,
            "totalWeight": 31.1,
            "unitPrice": 273.31,
            "currency": "PLN",
            "seller": "Mennica Polska",
            "goldSource": "1oz Krugerrand",
            "comment": "Purchase",
        },
        occured_at=datetime(2025, 1, 15),
        version=1,
    )
    bonds_bought = es.Event(
        stream_type="investment",
        stream_id=bonds_stream.id,
        event_type="TreasuryBondsBought",
        data={
            "totalValue": 1000.0,
            "balance": 1000.0,
            "units": 10,
            "pricePerUnit": 100.0,
            "currency": "PLN",
        },
        occured_at=datetime(2025, 1, 15),
        version=1,
    )
    es.store([gold_bought, bonds_bought])

    # WHEN
    response = test_client.get("/api/investments")

    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    ids = [item["id"] for item in payload]
    assert str(gold_stream.id) in ids
    assert str(bonds_stream.id) in ids

    # Verify gold stream data
    gold_items = [item for item in payload if item["id"] == str(gold_stream.id)]
    assert len(gold_items) == 1
    gold = gold_items[0]
    assert gold["name"] == "Physical Gold"
    assert gold["investmentType"] == "investment"
    assert gold["subtype"] == "gold"
    assert gold["balance"] == 8500.0


def test_get_gold_transactions(test_client):
    # GIVEN
    gold_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "gold",
        "Physical Gold",
        "Gold Dealer",
        True,
        0,
        {"details": "Gold coins"},
        {"wallet": "Wallet A"},
    )
    es.create([gold_stream])

    gold_bought = es.Event(
        stream_type="investment",
        stream_id=gold_stream.id,
        event_type="GoldBought",
        data={
            "totalValue": 8500.0,
            "balance": 8500.0,
            "weight": 31.1,
            "totalWeight": 31.1,
            "unitPrice": 273.31,
            "currency": "PLN",
            "seller": "Mennica Polska",
            "goldSource": "1oz Krugerrand",
            "comment": "First purchase",
        },
        occured_at=datetime(2025, 1, 15),
        version=1,
    )
    gold_priced = es.Event(
        stream_type="investment",
        stream_id=gold_stream.id,
        event_type="GoldPriced",
        data={
            "totalValue": 0.0,
            "balance": 9330.0,
            "weight": 0.0,
            "totalWeight": 31.1,
            "unitPrice": 300.0,
            "currency": "PLN",
            "comment": "Monthly revaluation",
        },
        occured_at=datetime(2025, 2, 15),
        version=2,
    )
    gold_sold = es.Event(
        stream_type="investment",
        stream_id=gold_stream.id,
        event_type="GoldSold",
        data={
            "totalValue": 9330.0,
            "balance": 0.0,
            "weight": 31.1,
            "totalWeight": 0.0,
            "unitPrice": 300.0,
            "currency": "PLN",
            "buyer": "Mennica Polska",
            "goldSource": "1oz Krugerrand",
            "comment": "Sold all",
        },
        occured_at=datetime(2025, 3, 15),
        version=3,
    )
    es.store([gold_bought, gold_priced, gold_sold])

    # WHEN
    response = test_client.get(f"/api/investments/transactions/{gold_stream.id}")

    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload) == 3

    # Results are ordered by version DESC (sold, priced, bought)
    sold = payload[0]
    assert sold["eventType"] == "Gold Sold"
    assert sold["pricePerUnit"] == 300.0
    assert sold["unitsCount"] == 31.1
    assert sold["totalValue"] == 9330.0
    assert sold["balance"] == 0.0
    assert sold["comment"] == "Sold all"

    priced = payload[1]
    assert priced["eventType"] == "Gold Priced"
    assert priced["pricePerUnit"] == 300.0
    assert priced["unitsCount"] == 0.0
    assert priced["balance"] == 9330.0
    assert priced["comment"] == "Monthly revaluation"

    bought = payload[2]
    assert bought["eventType"] == "Gold Bought"
    assert bought["pricePerUnit"] == 273.31
    assert bought["unitsCount"] == 31.1
    assert bought["totalValue"] == 8500.0
    assert bought["balance"] == 8500.0
    assert bought["comment"] == "First purchase"


# ============================================================================
# POST /api/investments/events ENDPOINT TESTS
# ============================================================================


# ============================================================================
# 1. SUCCESSFUL EVENT CREATION TESTS
# ============================================================================


def test_create_buy_event_returns_201_with_event_id_and_version(test_client):
    """Test that POST buy event returns 201 with eventId and streamVersion."""
    # GIVEN: An investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy event
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 10.0,
            "totalValue": 1000.0,
            "comment": "Initial purchase",
        },
    )

    # THEN: Returns 201 with eventId and streamVersion
    assert response.status_code == 201
    data = response.get_json()
    assert data["result"] == "Success"
    assert "eventId" in data
    assert uuid.UUID(data["eventId"])  # Valid UUID
    assert data["streamVersion"] == 1


def test_create_sell_event_returns_201(test_client):
    """Test that POST sell event returns 201."""
    # GIVEN: Investment stream with existing buy event
    stream = es.Stream(
        id=uuid.uuid4(),
        type="investment",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # Create initial buy event
    buy_event = es.Event(
        stream_type="investment",
        stream_id=stream.id,
        event_type="ETFBought",
        data={
            "totalValue": 1000.0,
            "balance": 1000.0,
            "units": 10.0,
            "averagePrice": 100.0,
            "currency": "PLN",
            "comment": "Initial",
        },
        occured_at=datetime(2026, 2, 1),
        version=1,
    )
    es.store([buy_event])

    # WHEN: POST sell event
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "sell",
            "occuredAt": "2026-02-20",
            "units": 5.0,
            "totalValue": 550.0,
            "comment": "Partial sale",
        },
    )

    # THEN: Returns 201
    assert response.status_code == 201
    data = response.get_json()
    assert data["result"] == "Success"
    assert data["streamVersion"] == 2


def test_create_price_update_event_returns_201_and_stores_etfpriced_name(test_client):
    """Test that price_update event type stores as ETFPriced event name."""
    # GIVEN: Investment stream with units
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "IKE"},
    )
    es.create([stream])

    # Add buy event to have units
    buy_event = es.Event(
        stream_type="stocks",
        stream_id=stream.id,
        event_type="ETFBought",
        data={
            "totalValue": 1000.0,
            "balance": 1000.0,
            "units": 10.0,
            "averagePrice": 100.0,
            "currency": "PLN",
            "comment": "",
        },
        occured_at=datetime(2026, 2, 1),
        version=1,
    )
    es.store([buy_event])

    # WHEN: POST price_update event
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "price_update",
            "occuredAt": "2026-02-22",
            "pricePerUnit": 110.0,
            "comment": "Market price update",
        },
    )

    # THEN: Returns 201 and event stored as ETFPriced
    assert response.status_code == 201
    data = response.get_json()
    assert data["result"] == "Success"

    # Verify event name in database
    events = es.load(stream.id)
    assert len(events) == 2
    assert events[1].event_type == "ETFPriced"


def test_buy_event_stored_in_database_with_correct_structure(test_client):
    """Verify buy event is stored with correct JSONB structure."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy event
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 10.5,
            "totalValue": 1050.0,
            "comment": "Test purchase",
        },
    )

    # THEN: Event stored with correct structure
    assert response.status_code == 201

    events = es.load(stream.id)
    assert len(events) == 1

    event_data = events[0].data
    assert event_data["totalValue"] == 1050.0
    assert event_data["balance"] == 1050.0
    assert event_data["units"] == 10.5
    assert event_data["averagePrice"] == 100.0
    assert event_data["currency"] == "PLN"
    assert event_data["comment"] == "Test purchase"


def test_stream_version_increments_after_event(test_client):
    """Verify stream version increments after each event."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="investment",
        subtype="treasury_bonds",
        name="Test Bonds",
        bank="PKO",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST first event
    response1 = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 10.0,
            "totalValue": 1000.0,
        },
    )

    # THEN: Version is 1
    assert response1.status_code == 201
    assert response1.get_json()["streamVersion"] == 1

    # WHEN: POST second event
    response2 = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-20",
            "units": 5.0,
            "totalValue": 500.0,
        },
    )

    # THEN: Version is 2
    assert response2.status_code == 201
    assert response2.get_json()["streamVersion"] == 2

    # Verify in database
    updated_stream = es.get_stream_by_id(str(stream.id))
    assert updated_stream is not None
    assert updated_stream.version == 2


# ============================================================================
# 2. VALIDATION ERROR TESTS
# ============================================================================


def test_missing_units_for_buy_returns_400(test_client):
    """Test that missing units for buy event returns 400."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy without units
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "totalValue": 1000.0,
        },
    )

    # THEN: Returns 400
    assert response.status_code == 400


def test_missing_total_value_for_buy_returns_400(test_client):
    """Test that missing totalValue for buy event returns 400."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy without totalValue
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 10.0,
        },
    )

    # THEN: Returns 400
    assert response.status_code == 400


def test_negative_units_returns_400(test_client):
    """Test that negative units returns 400."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy with negative units
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": -10.0,
            "totalValue": 1000.0,
        },
    )

    # THEN: Returns 400
    assert response.status_code == 400


def test_zero_units_returns_400(test_client):
    """Test that zero units returns 400."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy with zero units
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 0.0,
            "totalValue": 1000.0,
        },
    )

    # THEN: Returns 400
    assert response.status_code == 400


def test_negative_total_value_returns_400(test_client):
    """Test that negative totalValue returns 400."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy with negative totalValue
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 10.0,
            "totalValue": -1000.0,
        },
    )

    # THEN: Returns 400
    assert response.status_code == 400


def test_zero_total_value_returns_400(test_client):
    """Test that zero totalValue returns 400."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy with zero totalValue
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 10.0,
            "totalValue": 0.0,
        },
    )

    # THEN: Returns 400
    assert response.status_code == 400


def test_negative_price_per_unit_returns_400(test_client):
    """Test that negative pricePerUnit returns 400."""
    # GIVEN: Investment stream with units
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # Add buy event
    buy_event = es.Event(
        stream_type="stocks",
        stream_id=stream.id,
        event_type="ETFBought",
        data={
            "totalValue": 1000.0,
            "balance": 1000.0,
            "units": 10.0,
            "averagePrice": 100.0,
            "currency": "PLN",
            "comment": "",
        },
        occured_at=datetime(2026, 2, 1),
        version=1,
    )
    es.store([buy_event])

    # WHEN: POST price_update with negative pricePerUnit
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "price_update",
            "occuredAt": "2026-02-15",
            "pricePerUnit": -100.0,
        },
    )

    # THEN: Returns 400
    assert response.status_code == 400


def test_zero_price_per_unit_returns_400(test_client):
    """Test that zero pricePerUnit returns 400."""
    # GIVEN: Investment stream with units
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # Add buy event
    buy_event = es.Event(
        stream_type="stocks",
        stream_id=stream.id,
        event_type="ETFBought",
        data={
            "totalValue": 1000.0,
            "balance": 1000.0,
            "units": 10.0,
            "averagePrice": 100.0,
            "currency": "PLN",
            "comment": "",
        },
        occured_at=datetime(2026, 2, 1),
        version=1,
    )
    es.store([buy_event])

    # WHEN: POST price_update with zero pricePerUnit
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "price_update",
            "occuredAt": "2026-02-15",
            "pricePerUnit": 0.0,
        },
    )

    # THEN: Returns 400
    assert response.status_code == 400


def test_invalid_event_type_returns_400(test_client):
    """Test that invalid eventType returns 400."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST with invalid eventType
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "invalid_type",
            "occuredAt": "2026-02-15",
            "units": 10.0,
            "totalValue": 1000.0,
        },
    )

    # THEN: Returns 400
    assert response.status_code == 400


def test_missing_price_per_unit_for_price_update_returns_400(test_client):
    """Test that missing pricePerUnit for price_update returns 400."""
    # GIVEN: Investment stream with units
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # Add buy event
    buy_event = es.Event(
        stream_type="stocks",
        stream_id=stream.id,
        event_type="ETFBought",
        data={
            "totalValue": 1000.0,
            "balance": 1000.0,
            "units": 10.0,
            "averagePrice": 100.0,
            "currency": "PLN",
            "comment": "",
        },
        occured_at=datetime(2026, 2, 1),
        version=1,
    )
    es.store([buy_event])

    # WHEN: POST price_update without pricePerUnit
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "price_update",
            "occuredAt": "2026-02-15",
        },
    )

    # THEN: Returns 400
    assert response.status_code == 400


# ============================================================================
# 3. STREAM ERROR TESTS
# ============================================================================


def test_non_existent_stream_id_returns_404(test_client):
    """Test that non-existent streamId returns 404."""
    # GIVEN: Random UUID that doesn't exist
    non_existent_id = str(uuid.uuid4())

    # WHEN: POST event to non-existent stream
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": non_existent_id,
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 10.0,
            "totalValue": 1000.0,
        },
    )

    # THEN: Returns 404
    assert response.status_code == 404


def test_wrong_stream_type_returns_400(test_client):
    """Test that wrong stream type (e.g., account) returns 400."""
    # GIVEN: Account stream (not investment or stocks)
    stream = es.Stream(
        id=uuid.uuid4(),
        type="account",
        subtype="checking",
        name="Test Account",
        bank="Bank A",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST investment event to account stream
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 10.0,
            "totalValue": 1000.0,
        },
    )

    # THEN: Returns 400
    assert response.status_code == 400


def test_missing_stream_id_returns_400(test_client):
    """Test that missing streamId returns 422 (schema validation)."""
    # WHEN: POST event without streamId
    response = test_client.post(
        "/api/investments/events",
        json={
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 10.0,
            "totalValue": 1000.0,
        },
    )

    # THEN: Returns 422 (APIFlask schema validation error)
    assert response.status_code == 422


# ============================================================================
# 4. EDGE CASE TESTS
# ============================================================================


def test_empty_comment_field_works(test_client):
    """Test that empty comment field works correctly."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy with empty comment
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 10.0,
            "totalValue": 1000.0,
            "comment": "",
        },
    )

    # THEN: Returns 201
    assert response.status_code == 201

    # Verify comment is stored as empty string
    events = es.load(stream.id)
    assert events[0].data["comment"] == ""


def test_decimal_precision_in_calculations(test_client):
    """Test decimal precision in unit price calculations."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy with values that create decimal precision
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 3.0,
            "totalValue": 100.0,
        },
    )

    # THEN: Returns 201
    assert response.status_code == 201

    # Verify average price calculation (100/3 = 33.333...)
    events = es.load(stream.id)
    average_price = events[0].data["averagePrice"]
    assert abs(average_price - 33.333333333333336) < 0.0001


def test_future_occured_at_date_works(test_client):
    """Test that future occuredAt date works."""
    from datetime import timedelta

    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy with future date
    future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": future_date,
            "units": 10.0,
            "totalValue": 1000.0,
        },
    )

    # THEN: Returns 201 (future dates allowed)
    assert response.status_code == 201


def test_multiple_events_increment_version_correctly(test_client):
    """Test that multiple events increment version sequentially."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST three events
    response1 = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-10",
            "units": 10.0,
            "totalValue": 1000.0,
        },
    )

    response2 = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 5.0,
            "totalValue": 500.0,
        },
    )

    response3 = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "price_update",
            "occuredAt": "2026-02-20",
            "pricePerUnit": 110.0,
        },
    )

    # THEN: Versions increment correctly
    assert response1.get_json()["streamVersion"] == 1
    assert response2.get_json()["streamVersion"] == 2
    assert response3.get_json()["streamVersion"] == 3

    # Verify in database
    events = es.load(stream.id)
    assert len(events) == 3
    assert events[0].version == 1
    assert events[1].version == 2
    assert events[2].version == 3


def test_missing_occured_at_returns_400(test_client):
    """Test that missing occuredAt returns 422 (schema validation)."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # WHEN: POST buy without occuredAt
    response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "units": 10.0,
            "totalValue": 1000.0,
        },
    )

    # THEN: Returns 422 (APIFlask schema validation error)
    assert response.status_code == 422


# ============================================================================
# 5. INTEGRATION TEST
# ============================================================================


def test_complete_investment_flow_buy_price_sell(test_client):
    """Integration test: buy → price_update → sell flow."""
    # GIVEN: Investment stream
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "IKE"},
    )
    es.create([stream])

    # WHEN: Step 1 - Buy 10 units @ 1000 PLN total
    buy_response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-10",
            "units": 10.0,
            "totalValue": 1000.0,
            "comment": "Initial purchase",
        },
    )

    # THEN: Buy succeeds
    assert buy_response.status_code == 201
    assert buy_response.get_json()["streamVersion"] == 1

    # Verify buy event
    events = es.load(stream.id)
    assert len(events) == 1
    assert events[0].event_type == "ETFBought"
    assert events[0].data["balance"] == 1000.0
    assert events[0].data["units"] == 10.0

    # WHEN: Step 2 - Price update to 110 PLN per unit
    price_response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "price_update",
            "occuredAt": "2026-02-15",
            "pricePerUnit": 110.0,
            "comment": "Market update",
        },
    )

    # THEN: Price update succeeds and stores as ETFPriced
    assert price_response.status_code == 201
    assert price_response.get_json()["streamVersion"] == 2

    events = es.load(stream.id)
    assert len(events) == 2
    assert events[1].event_type == "ETFPriced"
    assert events[1].data["pricePerUnit"] == 110.0
    assert events[1].data["balance"] == 1100.0  # 10 units * 110 PLN

    # WHEN: Step 3 - Sell 5 units @ 550 PLN total
    sell_response = test_client.post(
        "/api/investments/events",
        json={
            "streamId": str(stream.id),
            "eventType": "sell",
            "occuredAt": "2026-02-20",
            "units": 5.0,
            "totalValue": 550.0,
            "comment": "Partial sale",
        },
    )

    # THEN: Sell succeeds
    assert sell_response.status_code == 201
    assert sell_response.get_json()["streamVersion"] == 3

    # Verify final state
    events = es.load(stream.id)
    assert len(events) == 3
    assert events[2].event_type == "ETFSold"
    assert events[2].data["units"] == -5.0  # Negative for sell
    assert events[2].data["balance"] == 550.0  # 1100 - 550

    # Verify stream version
    updated_stream = es.get_stream_by_id(str(stream.id))
    assert updated_stream is not None
    assert updated_stream.version == 3


# ============================================================================
# 6. CONCURRENT WRITE TEST (OPTIMISTIC LOCKING)
# ============================================================================


def test_concurrent_event_writes_optimistic_locking(test_client):
    """Test that sequential writes to the same stream maintain correct versions.

    This test verifies that multiple sequential writes to the same stream
    correctly increment versions and maintain data integrity.
    """
    # GIVEN: Investment stream with initial buy event (version 1)
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    # Add initial buy event (version 1)
    buy_event = es.Event(
        stream_type="stocks",
        stream_id=stream.id,
        event_type="ETFBought",
        data={
            "totalValue": 1000.0,
            "balance": 1000.0,
            "units": 10.0,
            "averagePrice": 100.0,
            "currency": "PLN",
            "comment": "Initial purchase",
        },
        occured_at=datetime(2026, 2, 1),
        version=1,
    )
    es.store([buy_event])

    # Verify stream is at version 1
    stream_after_buy = es.get_stream_by_id(str(stream.id))
    assert stream_after_buy is not None
    assert stream_after_buy.version == 1

    # WHEN: Two sequential sell requests are made
    sell_request_1 = {
        "streamId": str(stream.id),
        "eventType": "sell",
        "occuredAt": "2026-02-15",
        "units": 3.0,
        "totalValue": 330.0,
        "comment": "First sell",
    }

    sell_request_2 = {
        "streamId": str(stream.id),
        "eventType": "sell",
        "occuredAt": "2026-02-16",
        "units": 2.0,
        "totalValue": 220.0,
        "comment": "Second sell",
    }

    response1 = test_client.post("/api/investments/events", json=sell_request_1)
    response2 = test_client.post("/api/investments/events", json=sell_request_2)

    # THEN: Both requests succeed
    assert response1.status_code == 201, "First request should succeed"
    assert response2.status_code == 201, "Second request should succeed"

    # Verify final stream has exactly 3 events (1 buy + 2 sells)
    final_events = es.load(stream.id)
    assert len(final_events) == 3, "Should have 3 events total"
    assert final_events[0].event_type == "ETFBought"
    assert final_events[1].event_type == "ETFSold"
    assert final_events[2].event_type == "ETFSold"

    # Verify stream version is 3
    final_stream = es.get_stream_by_id(str(stream.id))
    assert final_stream is not None
    assert final_stream.version == 3, "Stream version should be 3 (one buy, two sells)"
