import time
import uuid
from datetime import datetime

import mankkoo.app as app
import mankkoo.data_for_test as dt
import mankkoo.event_store as es
import mankkoo.views as views

checking_operations = [
    {"date": "02-01-2021", "operation": 1000},
    # operations at the same day, including multiple accounts i.e. savings
    {"date": "02-01-2021", "operation": -333.23},
    {"date": "05-01-2021", "operation": 67.90},
    {"date": "05-01-2021", "operation": -8.90},
    # multiple operations for the same account
    {"date": "05-01-2021", "operation": -200},
    {"date": "06-01-2021", "operation": -100},  # buy and investment item
    # put money on retirement account, one day gap
    {"date": "09-01-2021", "operation": -55.55},
]

stock_operations = [{"date": "02-01-2021", "operation": 333.23}]

savings_operations = [{"date": "04-01-2021", "operation": 145.78}]

investment_operations = [{"date": "06-01-2021", "operation": 100}]

retirment_operations = [{"date": "09-01-2021", "operation": 55.55}]

checking_events = dt.an_account_with_operations(checking_operations)
savings_events = dt.an_account_with_operations(savings_operations, type="savings")
stock_events = dt.stock_events(stock_operations)
investment_events = dt.investment_events(investment_operations)
retirement_events = dt.retirment_events(retirment_operations)


def test_view_is_loaded():
    # GIVEN
    app.start_listener_thread()
    __store_events()

    # WHEN
    def a_view_is_loaded():
        result = views.load_view(views.main_indicators_key)
        return result is not None

    # THEN
    __wait_for_condition(condition_func=a_view_is_loaded, timeout=10, interval=1)


def test_view_is_not_loaded_if_incorrect_name_was_provided():
    # GIVEN
    app.start_listener_thread()
    __store_events()

    # WHEN
    assert views.load_view("invalid-view-name") is None


def test_main_indicators_view_is_updated():
    # GIVEN
    app.start_listener_thread()
    __store_events()

    # WHEN
    def a_main_indicators_view_is_updated():
        result = views.load_view(views.main_indicators_key)
        return result == {
            "lastMonthIncome": None,
            "lastMonthSpending": None,
            "netWorth": None,
            "savings": 1004.78,
        }

    # THEN
    __wait_for_condition(
        condition_func=a_main_indicators_view_is_updated, timeout=10, interval=1
    )


def test_current_total_savings_distribution_view_is_updated():
    # GIVEN
    app.start_listener_thread()
    __store_events()

    # WHEN
    def a_current_total_savings_distribution_view_is_updated():
        result = views.load_view(views.current_savings_distribution_key)
        return result == [
            {
                "type": "Checking Accounts",
                "total": 370.21999999999997,
                "percentage": 0.3685,
            },
            {"type": "Savings Accounts", "total": 145.78, "percentage": 0.1451},
            {"type": "Investments", "total": 100, "percentage": 0.0995},
            {"type": "Stocks & ETFs", "total": 333.23, "percentage": 0.3316},
            {"type": "Retirement", "total": 55.55, "percentage": 0.0553},
        ]

    # THEN
    __wait_for_condition(
        condition_func=a_current_total_savings_distribution_view_is_updated,
        timeout=10,
        interval=1,
    )


def test_total_history_per_day_is_updated():
    # GIVEN
    app.start_listener_thread()
    __store_events()

    # WHEN
    def a_total_history_per_day_view_is_updated():
        result = views.load_view(views.total_history_per_day_key)
        return result == {
            "date": [
                "2021-01-09",
                "2021-01-08",
                "2021-01-07",
                "2021-01-06",
                "2021-01-05",
                "2021-01-04",
                "2021-01-03",
                "2021-01-02",
                "2021-01-01",
            ],
            "total": [
                1004.78,
                1004.78,
                1004.78,
                1004.78,
                1004.78,
                1145.78,
                1000,
                1000,
                0,
            ],
        }

    # THEN
    __wait_for_condition(
        condition_func=a_total_history_per_day_view_is_updated, timeout=10, interval=1
    )


def test_investment_types_distribution_view_is_updated():
    # GIVEN
    app.start_listener_thread()
    # Prepare events: active/inactive investments and stocks
    active_investment_events = dt.investment_events(
        [{"date": "01-01-2021", "operation": 100}],
        category="treasury_bonds",
        active=True,
    )
    inactive_investment_events = dt.investment_events(
        [{"date": "01-01-2021", "operation": 200}], category="crypto", active=False
    )
    active_stock_events = dt.stock_events(
        [{"date": "01-01-2021", "operation": 300}], type="ETF", active=True
    )
    inactive_stock_events = dt.stock_events(
        [{"date": "01-01-2021", "operation": 400}], type="stock", active=False
    )

    es.create(
        [
            active_investment_events["stream"],
            inactive_investment_events["stream"],
            active_stock_events["stream"],
            inactive_stock_events["stream"],
        ]
    )
    es.store(
        active_investment_events["events"]
        + inactive_investment_events["events"]
        + active_stock_events["events"]
        + inactive_stock_events["events"]
    )

    # WHEN
    def a_investment_types_distribution_view_is_updated():
        result = views.load_view(views.investment_types_distribution_key)
        # Only active streams should be included: 100 (bonds) + 300 (ETF) = 400
        # bonds: 100/400 = 0.25, ETF: 300/400 = 0.75
        expected = [
            {"type": "Etf", "total": 300, "percentage": 0.75},
            {"type": "Treasury Bonds", "total": 100, "percentage": 0.25},
        ]
        # Order by total desc
        return result == expected

    # THEN
    __wait_for_condition(
        condition_func=a_investment_types_distribution_view_is_updated,
        timeout=10,
        interval=1,
    )


def test_investment_wallets_distribution_view_is_updated():
    # GIVEN
    app.start_listener_thread()
    # Prepare events: active/inactive investments, stocks, and savings, with
    # wallets
    active_investment_events = dt.investment_events(
        [{"date": "01-01-2021", "operation": 100}],
        category="treasury_bonds",
        active=True,
        wallet="Cat",
    )
    inactive_investment_events = dt.investment_events(
        [{"date": "01-01-2021", "operation": 200}],
        category="crypto",
        active=False,
        wallet="Cat",
    )
    active_stock_events = dt.stock_events(
        [{"date": "01-01-2021", "operation": 300}],
        type="ETF",
        active=True,
        wallet="Cat",
    )
    inactive_stock_events = dt.stock_events(
        [{"date": "01-01-2021", "operation": 400}],
        type="stock",
        active=False,
        wallet="Puppy",
    )
    active_savings_events = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 500}],
        type="savings",
        active=True,
        wallet="Puppy",
    )
    inactive_savings_events = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 600}],
        type="savings",
        active=False,
        wallet="Cat",
    )

    es.create(
        [
            active_investment_events["stream"],
            inactive_investment_events["stream"],
            active_stock_events["stream"],
            inactive_stock_events["stream"],
            active_savings_events["stream"],
            inactive_savings_events["stream"],
        ]
    )
    es.store(
        active_investment_events["events"]
        + inactive_investment_events["events"]
        + active_stock_events["events"]
        + inactive_stock_events["events"]
        + active_savings_events["events"]
        + inactive_savings_events["events"]
    )

    # WHEN
    def a_investment_wallets_distribution_view_is_updated():
        result = views.load_view(views.investment_wallets_distribution_key)
        # Only active streams should be included: Cat: 100 (investment) + 300 (stock) = 400, Puppy: 500 (savings)
        # Total = 900
        # Cat: 400/900 = 0.9948, Puppy: 500/900 = 0.0052
        expected = [
            {"wallet": "Puppy", "total": 500, "percentage": round(500 / 900, 4)},
            {"wallet": "Cat", "total": 400, "percentage": round(400 / 900, 4)},
        ]
        # Order by total desc
        return result == expected

    # THEN
    __wait_for_condition(
        condition_func=a_investment_wallets_distribution_view_is_updated,
        timeout=10,
        interval=1,
    )


def test_investment_types_distribution_per_wallet_view_is_updated():
    # GIVEN
    app.start_listener_thread()
    # Prepare events: active/inactive investments, stocks, and savings, with
    # wallets
    active_investment_events = dt.investment_events(
        [{"date": "01-01-2021", "operation": 100}],
        category="treasury_bonds",
        active=True,
        wallet="Cat",
    )
    inactive_investment_events = dt.investment_events(
        [{"date": "01-01-2021", "operation": 200}],
        category="crypto",
        active=False,
        wallet="Cat",
    )
    active_stock_events = dt.stock_events(
        [{"date": "01-01-2021", "operation": 300}],
        type="ETF",
        active=True,
        wallet="Cat",
    )
    inactive_stock_events = dt.stock_events(
        [{"date": "01-01-2021", "operation": 400}],
        type="stock",
        active=False,
        wallet="Puppy",
    )
    active_savings_events = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 500}],
        type="savings",
        active=True,
        wallet="Puppy",
    )
    inactive_savings_events = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 600}],
        type="savings",
        active=False,
        wallet="Cat",
    )

    es.create(
        [
            active_investment_events["stream"],
            inactive_investment_events["stream"],
            active_stock_events["stream"],
            inactive_stock_events["stream"],
            active_savings_events["stream"],
            inactive_savings_events["stream"],
        ]
    )
    es.store(
        active_investment_events["events"]
        + inactive_investment_events["events"]
        + active_stock_events["events"]
        + inactive_stock_events["events"]
        + active_savings_events["events"]
        + inactive_savings_events["events"]
    )

    # WHEN
    def a_investment_types_distribution_per_wallet_view_is_updated():
        result = views.load_view(views.investment_types_distribution_per_wallet_key)
        # Only active streams should be included:
        # Cat: 100 (treasury_bonds) + 300 (ETF)
        # Puppy: 500 (savings)
        # For Cat: total = 400, Puppy: total = 500
        # Cat: treasury_bonds: 100/400 = 0.25, ETF: 300/400 = 0.75
        # Puppy: savings: 500/500 = 1.0
        expected = [
            {"wallet": "Cat", "type": "Etf", "total": 300, "percentage": 0.75},
            {
                "wallet": "Cat",
                "type": "Treasury Bonds",
                "total": 100,
                "percentage": 0.25,
            },
            {
                "wallet": "Puppy",
                "type": "Savings Accounts",
                "total": 500,
                "percentage": 1.0,
            },
        ]
        # Order by wallet, then total desc
        return result == expected

    # THEN
    __wait_for_condition(
        condition_func=a_investment_types_distribution_per_wallet_view_is_updated,
        timeout=10,
        interval=1,
    )


def test_investment_indicators_include_gold():
    # GIVEN
    app.start_listener_thread()

    # Create a gold stream with a GoldBought event
    gold_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "gold",
        "Physical Gold",
        "Gold Dealer",
        True,
        0,
        {"details": "Gold coins"},
        {"wallet": "Default"},
    )

    # Create a treasury bonds stream for baseline
    bonds_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "treasury_bonds",
        "10-years Treasury Bonds",
        "Bank 1",
        True,
        0,
        {"details": "Some details"},
        {"wallet": "Default"},
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
    def investment_indicators_include_gold_balance():
        result = views.load_view(views.investment_indicators_key)
        if result is None:
            return False
        # Gold (8500) + Bonds (1000) = 9500
        return result["totalInvestments"] == 9500.0

    # THEN
    __wait_for_condition(
        condition_func=investment_indicators_include_gold_balance,
        timeout=10,
        interval=1,
    )


def test_investment_types_distribution_includes_gold():
    # GIVEN
    app.start_listener_thread()

    gold_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "gold",
        "Physical Gold",
        "Gold Dealer",
        True,
        0,
        {"details": "Gold coins"},
        {"wallet": "Default"},
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
        {"wallet": "Default"},
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
    def investment_types_distribution_includes_gold():
        result = views.load_view(views.investment_types_distribution_key)
        if result is None:
            return False
        # Total = 8500 + 1000 = 9500
        # Gold: 8500/9500 = 0.8947, Bonds: 1000/9500 = 0.1053
        expected = [
            {"type": "Gold", "total": 8500.0, "percentage": round(8500 / 9500, 4)},
            {
                "type": "Treasury Bonds",
                "total": 1000,
                "percentage": round(1000 / 9500, 4),
            },
        ]
        return result == expected

    # THEN
    __wait_for_condition(
        condition_func=investment_types_distribution_includes_gold,
        timeout=10,
        interval=1,
    )


def test_gold_lifecycle_updates_views():
    # GIVEN
    app.start_listener_thread()

    gold_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "gold",
        "Physical Gold",
        "Gold Dealer",
        True,
        0,
        {"details": "Gold coins"},
        {"wallet": "Default"},
    )
    es.create([gold_stream])

    # Step 1: Buy gold
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
    es.store([gold_bought])

    # Wait for initial view update
    def gold_bought_reflected_in_indicators():
        result = views.load_view(views.investment_indicators_key)
        if result is None:
            return False
        return result["totalInvestments"] == 8500.0

    __wait_for_condition(
        condition_func=gold_bought_reflected_in_indicators,
        timeout=10,
        interval=1,
    )

    # Step 2: Reprice gold (price went up)
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
    es.store([gold_priced])

    def gold_priced_reflected_in_indicators():
        result = views.load_view(views.investment_indicators_key)
        if result is None:
            return False
        return result["totalInvestments"] == 9330.0

    __wait_for_condition(
        condition_func=gold_priced_reflected_in_indicators,
        timeout=10,
        interval=1,
    )

    # Step 3: Sell all gold
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
    es.store([gold_sold])

    def gold_sold_reflected_in_indicators():
        result = views.load_view(views.investment_indicators_key)
        if result is None:
            return False
        return result["totalInvestments"] == 0

    __wait_for_condition(
        condition_func=gold_sold_reflected_in_indicators,
        timeout=10,
        interval=1,
    )


def __store_events():
    es.create(
        [
            checking_events["stream"],
            savings_events["stream"],
            retirement_events["stream"],
            investment_events["stream"],
            stock_events["stream"],
        ]
    )

    es.store(
        checking_events["events"]
        + savings_events["events"]
        + retirement_events["events"]
        + investment_events["events"]
        + stock_events["events"]
    )


def __wait_for_condition(condition_func, timeout=10, interval=1):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    raise TimeoutError(f"Condition was not met within {timeout} seconds.")
