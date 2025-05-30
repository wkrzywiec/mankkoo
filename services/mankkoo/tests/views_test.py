import time

import mankkoo.app as app
import mankkoo.data_for_test as dt
import mankkoo.event_store as es
import mankkoo.views as views


checking_operations = [
    {"date": "02-01-2021", "operation": 1000},
    {"date": "02-01-2021", "operation": -333.23},   # operations at the same day, including multiple accounts i.e. savings
    {"date": "05-01-2021", "operation": 67.90},
    {"date": "05-01-2021", "operation": -8.90},
    {"date": "05-01-2021", "operation": -200},      # multiple operations for the same account
    {"date": "06-01-2021", "operation": -100},      # buy and investment item
    {"date": "09-01-2021", "operation": -55.55}     # put money on retirement account, one day gap
]

stock_operations = [
    {"date": "02-01-2021", "operation": 333.23}
]

savings_operations = [
    {"date": "04-01-2021", "operation": 145.78}
]

investment_operations = [
    {"date": "06-01-2021", "operation": 100}
]

retirment_operations = [
    {"date": "09-01-2021", "operation": 55.55}
]

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
    assert views.load_view('invalid-view-name') is None


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
    __wait_for_condition(condition_func=a_main_indicators_view_is_updated, timeout=10, interval=1)


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
                "percentage": 0.3685
            },
            {
                "type": "Savings Accounts",
                "total": 145.78,
                "percentage": 0.1451
            },
            {
                "type": "Investments",
                "total": 100,
                "percentage": 0.0995
            },
            {
                "type": "Stocks & ETFs",
                "total": 333.23,
                "percentage": 0.3316
            },
            {
                "type": "Retirement",
                "total": 55.55,
                "percentage": 0.0553
            }
        ]

    # THEN
    __wait_for_condition(condition_func=a_current_total_savings_distribution_view_is_updated, timeout=10, interval=1)


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
                "2021-01-01"
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
                0
            ]
        }

    # THEN
    __wait_for_condition(condition_func=a_total_history_per_day_view_is_updated, timeout=10, interval=1)


def test_investment_types_distribution_view_is_updated():
    # GIVEN
    app.start_listener_thread()
    # Prepare events: active/inactive investments and stocks
    active_investment_events = dt.investment_events([
        {"date": "01-01-2021", "operation": 100}
    ], category="treasury_bonds", active=True)
    inactive_investment_events = dt.investment_events([
        {"date": "01-01-2021", "operation": 200}
    ], category="crypto", active=False)
    active_stock_events = dt.stock_events([
        {"date": "01-01-2021", "operation": 300}
    ], type="ETF", active=True)
    inactive_stock_events = dt.stock_events([
        {"date": "01-01-2021", "operation": 400}
    ], type="stock", active=False)

    es.create([
        active_investment_events['stream'],
        inactive_investment_events['stream'],
        active_stock_events['stream'],
        inactive_stock_events['stream']
    ])
    es.store(
        active_investment_events['events'] +
        inactive_investment_events['events'] +
        active_stock_events['events'] +
        inactive_stock_events['events']
    )

    # WHEN
    def a_investment_types_distribution_view_is_updated():
        result = views.load_view(views.investment_types_distribution_key)
        # Only active streams should be included: 100 (bonds) + 300 (ETF) = 400
        # bonds: 100/400 = 0.25, ETF: 300/400 = 0.75
        expected = [
            {"type": "Etf", "total": 300, "percentage": 0.75},
            {"type": "Treasury Bonds", "total": 100, "percentage": 0.25}
        ]
        # Order by total desc
        return result == expected

    # THEN
    __wait_for_condition(condition_func=a_investment_types_distribution_view_is_updated, timeout=10, interval=1)


def test_investment_wallets_distribution_view_is_updated():
    # GIVEN
    app.start_listener_thread()
    # Prepare events: active/inactive investments, stocks, and savings, with wallets
    active_investment_events = dt.investment_events([
        {"date": "01-01-2021", "operation": 100}
    ], category="treasury_bonds", active=True, wallet="Cat")
    inactive_investment_events = dt.investment_events([
        {"date": "01-01-2021", "operation": 200}
    ], category="crypto", active=False, wallet="Cat")
    active_stock_events = dt.stock_events([
        {"date": "01-01-2021", "operation": 300}
    ], type="ETF", active=True, wallet="Cat")
    inactive_stock_events = dt.stock_events([
        {"date": "01-01-2021", "operation": 400}
    ], type="stock", active=False, wallet="Puppy")
    active_savings_events = dt.an_account_with_operations([
        {"date": "01-01-2021", "operation": 500}
    ], type="savings", active=True, wallet="Puppy")
    inactive_savings_events = dt.an_account_with_operations([
        {"date": "01-01-2021", "operation": 600}
    ], type="savings", active=False, wallet="Cat")

    es.create([
        active_investment_events['stream'],
        inactive_investment_events['stream'],
        active_stock_events['stream'],
        inactive_stock_events['stream'],
        active_savings_events['stream'],
        inactive_savings_events['stream']
    ])
    es.store(
        active_investment_events['events'] +
        inactive_investment_events['events'] +
        active_stock_events['events'] +
        inactive_stock_events['events'] +
        active_savings_events['events'] +
        inactive_savings_events['events']
    )

    # WHEN
    def a_investment_wallets_distribution_view_is_updated():
        result = views.load_view(views.investment_wallets_distribution_key)
        # Only active streams should be included: Cat: 100 (investment) + 300 (stock) = 400, Puppy: 500 (savings)
        # Total = 900
        # Cat: 400/900 = 0.9948, Puppy: 500/900 = 0.0052
        expected = [
            {"wallet": "Puppy", "total": 500, "percentage": round(500/900, 4)},
            {"wallet": "Cat", "total": 400, "percentage": round(400/900, 4)}
        ]
        # Order by total desc
        return result == expected

    # THEN
    __wait_for_condition(condition_func=a_investment_wallets_distribution_view_is_updated, timeout=10, interval=1)


def __store_events():
    es.create([
        checking_events['stream'],
        savings_events['stream'],
        retirement_events['stream'],
        investment_events['stream'],
        stock_events['stream']
    ])

    es.store(
        checking_events['events'] +
        savings_events['events'] +
        retirement_events['events'] +
        investment_events['events'] +
        stock_events['events']
    )


def __wait_for_condition(condition_func, timeout=10, interval=1):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    raise TimeoutError(f"Condition was not met within {timeout} seconds.")
