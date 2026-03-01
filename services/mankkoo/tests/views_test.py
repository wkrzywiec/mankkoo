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

retirement_operations = [{"date": "09-01-2021", "operation": 55.55}]

checking_events = dt.an_account_with_operations(checking_operations)
savings_events = dt.an_account_with_operations(savings_operations, type="savings")
stock_events = dt.stock_events(stock_operations)
investment_events = dt.investment_events(investment_operations)
retirement_events = dt.retirement_events(retirement_operations)


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


def test_excluded_streams_not_in_main_indicators():
    # GIVEN: Create accounts with one excluded from wealth calculations
    app.start_listener_thread()
    included_checking = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 1000}],
        type="checking",
        include_in_wealth=True,
    )
    excluded_checking = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 500}],
        type="checking",
        include_in_wealth=False,
    )

    es.create([included_checking["stream"], excluded_checking["stream"]])
    es.store(included_checking["events"] + excluded_checking["events"])

    # WHEN: Load the main indicators view
    def excluded_account_not_in_total():
        result = views.load_view(views.main_indicators_key)
        if result is None:
            return False
        # Should only include the 1000 from included account, not the 500 from
        # excluded
        return result["savings"] == 1000.0

    # THEN: Verify excluded stream is not included
    __wait_for_condition(
        condition_func=excluded_account_not_in_total, timeout=10, interval=1
    )


def test_excluded_streams_not_in_savings_distribution():
    # GIVEN: Create streams with mixed inclusion
    app.start_listener_thread()
    included_checking = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 500}],
        type="checking",
        include_in_wealth=True,
    )
    excluded_savings = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 300}],
        type="savings",
        include_in_wealth=False,
    )
    included_savings = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 200}],
        type="savings",
        include_in_wealth=True,
    )

    es.create(
        [
            included_checking["stream"],
            excluded_savings["stream"],
            included_savings["stream"],
        ]
    )
    es.store(
        included_checking["events"]
        + excluded_savings["events"]
        + included_savings["events"]
    )

    # WHEN: Load the current savings distribution view
    def excluded_streams_not_in_distribution():
        result = views.load_view(views.current_savings_distribution_key)
        if result is None:
            return False
        # Total should be 500 (checking) + 200 (savings) = 700, excluding the 300
        # Checking: 500/700 = 0.7143, Savings: 200/700 = 0.2857
        checking = next((r for r in result if r["type"] == "Checking Accounts"), None)
        savings = next((r for r in result if r["type"] == "Savings Accounts"), None)
        return (
            checking is not None
            and abs(checking["total"] - 500.0) < 0.01
            and savings is not None
            and abs(savings["total"] - 200.0) < 0.01
        )

    # THEN: Verify excluded streams are not in distribution
    __wait_for_condition(
        condition_func=excluded_streams_not_in_distribution, timeout=10, interval=1
    )


def test_excluded_investment_streams_not_in_investment_indicators():
    # GIVEN: Create investments with one excluded
    app.start_listener_thread()
    included_investment = dt.investment_events(
        [{"date": "01-01-2021", "operation": 500}],
        category="treasury_bonds",
        include_in_wealth=True,
    )
    excluded_investment = dt.investment_events(
        [{"date": "01-01-2021", "operation": 300}],
        category="crypto",
        include_in_wealth=False,
    )
    included_stock = dt.stock_events(
        [{"date": "01-01-2021", "operation": 200}], type="ETF", include_in_wealth=True
    )

    es.create(
        [
            included_investment["stream"],
            excluded_investment["stream"],
            included_stock["stream"],
        ]
    )
    es.store(
        included_investment["events"]
        + excluded_investment["events"]
        + included_stock["events"]
    )

    # WHEN: Load the investment indicators view
    def excluded_investments_not_in_indicators():
        result = views.load_view(views.investment_indicators_key)
        if result is None:
            return False
        # Should only sum: 500 (bonds) + 200 (stock) = 700, excluding 300
        # (crypto)
        return result["totalInvestments"] == 700.0

    # THEN: Verify excluded investments are not included
    __wait_for_condition(
        condition_func=excluded_investments_not_in_indicators, timeout=10, interval=1
    )


def test_excluded_streams_not_in_investment_types_distribution():
    # GIVEN: Create investments with mixed inclusion
    app.start_listener_thread()
    included_bonds = dt.investment_events(
        [{"date": "01-01-2021", "operation": 400}],
        category="treasury_bonds",
        include_in_wealth=True,
    )
    excluded_crypto = dt.investment_events(
        [{"date": "01-01-2021", "operation": 100}],
        category="crypto",
        include_in_wealth=False,
    )
    included_etf = dt.stock_events(
        [{"date": "01-01-2021", "operation": 300}], type="ETF", include_in_wealth=True
    )
    excluded_etf = dt.stock_events(
        [{"date": "01-01-2021", "operation": 50}], type="stock", include_in_wealth=False
    )

    es.create(
        [
            included_bonds["stream"],
            excluded_crypto["stream"],
            included_etf["stream"],
            excluded_etf["stream"],
        ]
    )
    es.store(
        included_bonds["events"]
        + excluded_crypto["events"]
        + included_etf["events"]
        + excluded_etf["events"]
    )

    # WHEN: Load the investment types distribution
    def excluded_types_not_in_distribution():
        result = views.load_view(views.investment_types_distribution_key)
        if result is None:
            return False
        # Total: 400 (bonds) + 300 (ETF) = 700, excluding 100 (crypto) and 50 (stock)
        # Bonds: 400/700 = 0.5714, ETF: 300/700 = 0.4286
        types = [r["type"] for r in result]
        # Should not include "Crypto" or "Stock", only "Treasury Bonds" and
        # "Etf"
        has_crypto = any(t == "Crypto" for t in types)
        has_stock = any(t == "Stock" for t in types)
        has_bonds = any(t == "Treasury Bonds" for t in types)
        has_etf = any(t == "Etf" for t in types)
        return not (has_crypto or has_stock) and has_bonds and has_etf

    # THEN: Verify excluded types are not in distribution
    __wait_for_condition(
        condition_func=excluded_types_not_in_distribution, timeout=10, interval=1
    )


def test_composition_views_include_excluded_streams():
    # GIVEN: Create streams with mixed wallets and inclusion flags
    app.start_listener_thread()
    included_wallet1 = dt.investment_events(
        [{"date": "01-01-2021", "operation": 100}],
        category="treasury_bonds",
        include_in_wealth=True,
        wallet="Wallet1",
    )
    excluded_wallet1 = dt.investment_events(
        [{"date": "01-01-2021", "operation": 200}],
        category="crypto",
        include_in_wealth=False,
        wallet="Wallet1",
    )
    included_wallet2 = dt.stock_events(
        [{"date": "01-01-2021", "operation": 150}],
        type="ETF",
        include_in_wealth=True,
        wallet="Wallet2",
    )
    excluded_wallet2 = dt.stock_events(
        [{"date": "01-01-2021", "operation": 50}],
        type="stock",
        include_in_wealth=False,
        wallet="Wallet2",
    )

    es.create(
        [
            included_wallet1["stream"],
            excluded_wallet1["stream"],
            included_wallet2["stream"],
            excluded_wallet2["stream"],
        ]
    )
    es.store(
        included_wallet1["events"]
        + excluded_wallet1["events"]
        + included_wallet2["events"]
        + excluded_wallet2["events"]
    )

    # WHEN: Load investment wallets distribution (composition view - should
    # include excluded)
    def composition_view_includes_all_streams():
        result = views.load_view(views.investment_wallets_distribution_key)
        if result is None:
            return False
        # Wallet1: 100 (included) + 200 (excluded) = 300
        # Wallet2: 150 (included) + 50 (excluded) = 200
        # Total = 500
        wallet1 = next((r for r in result if r["wallet"] == "Wallet1"), None)
        wallet2 = next((r for r in result if r["wallet"] == "Wallet2"), None)
        return (
            wallet1 is not None
            and abs(wallet1["total"] - 300.0) < 0.01
            and wallet2 is not None
            and abs(wallet2["total"] - 200.0) < 0.01
        )

    # THEN: Verify composition view includes excluded streams
    __wait_for_condition(
        condition_func=composition_view_includes_all_streams, timeout=10, interval=1
    )


def test_total_history_excludes_streams_at_each_date():
    # GIVEN: Create accounts with mixed inclusion that operate on different
    # dates
    app.start_listener_thread()
    included_account = dt.an_account_with_operations(
        [
            {"date": "01-01-2021", "operation": 100},
            {"date": "02-01-2021", "operation": 200},
            {"date": "03-01-2021", "operation": 300},
        ],
        type="checking",
        include_in_wealth=True,
    )
    excluded_account = dt.an_account_with_operations(
        [
            {"date": "01-01-2021", "operation": 50},
            {"date": "02-01-2021", "operation": 100},
            {"date": "03-01-2021", "operation": 150},
        ],
        type="savings",
        include_in_wealth=False,
    )

    es.create([included_account["stream"], excluded_account["stream"]])
    es.store(included_account["events"] + excluded_account["events"])

    # WHEN: Load the total history per day
    def history_excludes_at_each_date():
        result = views.load_view(views.total_history_per_day_key)
        if result is None or len(result["total"]) == 0:
            return False
        # Find the entry for 2021-01-03 (should be index 0 since ordered DESC)
        # Expected: 100 + 200 + 300 = 600 (excluded account not included)
        # 2021-01-02: 100 + 200 = 300
        # 2021-01-01: 100
        # Check if values are in descending order and match expected
        dates = result["date"]
        totals = result["total"]

        # Find indices for each date
        idx_03 = dates.index("2021-01-03") if "2021-01-03" in dates else None
        idx_02 = dates.index("2021-01-02") if "2021-01-02" in dates else None
        idx_01 = dates.index("2021-01-01") if "2021-01-01" in dates else None

        return (
            idx_03 is not None
            and abs(totals[idx_03] - 600.0) < 0.01
            and idx_02 is not None
            and abs(totals[idx_02] - 300.0) < 0.01
            and idx_01 is not None
            and abs(totals[idx_01] - 100.0) < 0.01
        )

    # THEN: Verify history excludes streams at each date
    __wait_for_condition(
        condition_func=history_excludes_at_each_date, timeout=10, interval=1
    )


def test_backward_compatibility_streams_without_flag_default_to_included():
    # GIVEN: Create a stream WITHOUT include_in_wealth flag and one WITH it
    app.start_listener_thread()
    no_flag_account = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 500}],
        type="checking",
        include_in_wealth=None,  # No flag set
    )
    included_account = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 300}],
        type="savings",
        include_in_wealth=True,
    )

    es.create([no_flag_account["stream"], included_account["stream"]])
    es.store(no_flag_account["events"] + included_account["events"])

    # WHEN: Load main indicators
    def backward_compatible_no_flag_defaults_to_true():
        result = views.load_view(views.main_indicators_key)
        if result is None:
            return False
        # Both should be included: 500 + 300 = 800
        return result["savings"] == 800.0

    # THEN: Verify streams without flag default to included
    __wait_for_condition(
        condition_func=backward_compatible_no_flag_defaults_to_true,
        timeout=10,
        interval=1,
    )


def test_composition_view_per_wallet_includes_excluded_streams():
    # GIVEN: Create streams with excluded items in different wallets
    app.start_listener_thread()
    included_bonds = dt.investment_events(
        [{"date": "01-01-2021", "operation": 100}],
        category="treasury_bonds",
        include_in_wealth=True,
        wallet="Wallet1",
    )
    excluded_crypto = dt.investment_events(
        [{"date": "01-01-2021", "operation": 200}],
        category="crypto",
        include_in_wealth=False,
        wallet="Wallet1",
    )
    included_savings = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 150}],
        type="savings",
        include_in_wealth=True,
        wallet="Wallet2",
    )
    excluded_savings = dt.an_account_with_operations(
        [{"date": "01-01-2021", "operation": 50}],
        type="savings",
        include_in_wealth=False,
        wallet="Wallet2",
    )

    es.create(
        [
            included_bonds["stream"],
            excluded_crypto["stream"],
            included_savings["stream"],
            excluded_savings["stream"],
        ]
    )
    es.store(
        included_bonds["events"]
        + excluded_crypto["events"]
        + included_savings["events"]
        + excluded_savings["events"]
    )

    # WHEN: Load per-wallet composition view
    def per_wallet_includes_excluded():
        result = views.load_view(views.investment_types_distribution_per_wallet_key)
        if result is None:
            return False
        # Wallet1: 100 (bonds) + 200 (crypto) = 300
        # Wallet2: 150 (savings) + 50 (savings) = 200
        wallet1_total = sum(r["total"] for r in result if r["wallet"] == "Wallet1")
        wallet2_total = sum(r["total"] for r in result if r["wallet"] == "Wallet2")
        return abs(wallet1_total - 300.0) < 0.01 and abs(wallet2_total - 200.0) < 0.01

    # THEN: Verify per-wallet composition includes excluded streams
    __wait_for_condition(
        condition_func=per_wallet_includes_excluded, timeout=10, interval=1
    )


def test_retirement_account_excluded_from_main_indicators():
    # GIVEN: Create retirement accounts with different inclusion flags
    app.start_listener_thread()
    included_retirement = dt.retirement_events(
        [{"date": "01-01-2021", "operation": 1000}]
    )
    # Manually set the inclusion flag for this retirement account
    excluded_retirement = dt.retirement_events(
        [{"date": "01-01-2021", "operation": 500}]
    )
    # Set exclude flag on the stream
    excluded_retirement["stream"].labels = {
        "wallet": "Default",
        "include_in_wealth": "false",
    }

    es.create([included_retirement["stream"], excluded_retirement["stream"]])
    es.store(included_retirement["events"] + excluded_retirement["events"])

    # WHEN: Load main indicators
    def retirement_excluded_works():
        result = views.load_view(views.main_indicators_key)
        if result is None:
            return False
        # Should only include 1000 from included retirement, not 500 from
        # excluded
        return result["savings"] == 1000.0

    # THEN: Verify excluded retirement not included
    __wait_for_condition(
        condition_func=retirement_excluded_works, timeout=10, interval=1
    )


def __wait_for_condition(condition_func, timeout=10, interval=1):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    raise TimeoutError(f"Condition was not met within {timeout} seconds.")
