import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import scripts.main.importer.importer as importer
import scripts.main.config as config
import scripts.main.models as models
from scripts.main.base_logger import log

def total_money_data(data: dict) -> pd.DataFrame:
    """Get summary data of all assets sorted by categories

    Args:
        data (dict): dictionary with all financial data

    Returns:
        pd.DataFrame: grouped financial standings
    """

    log.info('Fetching latest total money data')
    checking_account = __latest_account_balance(data, 'checking')
    savings_account = __latest_account_balance(data, 'savings')
    cash = __latest_account_balance(data, 'cash')
    ppk = __latest_account_balance(data, 'retirement')

    inv = data['investment'].loc[data['investment']['Active'] == True]
    inv = inv['Start Amount'].sum()

    stock_buy = data['stock'].loc[data['stock']['Operation'] == 'Buy']
    stock_buy = stock_buy['Total Value'].sum()
    stock_sell = data['stock'].loc[data['stock']['Operation'] == 'Sell']
    stock_sell = stock_sell['Total Value'].sum()
    stock = stock_buy - stock_sell
    # TODO check how much stock units I have Broker-Title pair buy-sell
    total = checking_account + savings_account + cash + ppk + inv + stock

    return pd.DataFrame([
        {'Type': 'Checking Account', 'Total': checking_account, 'Percentage': checking_account / total},
        {'Type': 'Savings Account', 'Total': savings_account, 'Percentage': savings_account / total},
        {'Type': 'Cash', 'Total': cash, 'Percentage': cash / total},
        {'Type': 'PPK', 'Total': ppk, 'Percentage': ppk / total},
        {'Type': 'Investments', 'Total': inv, 'Percentage': inv / total},
        {'Type': 'Stocks', 'Total': stock, 'Percentage': stock / total}
    ])

def __latest_account_balance(data: dict, type: str) -> float:

    df = data['account'].loc[data['account']['Type'] == type]
    if not df.empty:
        return accounts_balance_for_day(df, df['Date'].max())
    return 0.00

def update_total_money(accounts: pd.DataFrame, from_date: datetime.date, till_date = datetime.date.today()) -> pd.DataFrame:
    """Calculate and add rows of totals for each day from pd.Series

    Args:
        accounts (pd.DataFrame): updated accounts file
        updated_dates (pd.Series): Series of updated dates for which calculation needs to be done

    Returns:
        pd.DataFrame: new, updated total assets standing
    """
    log.info('Updating and calculating total money history from %s to %s', str(from_date), str(till_date))
    total = importer.load_data_from_file(models.FileType.TOTAL)

    total = __drop_from_total_days(total, from_date)
    total_new_lines = __calc_totals(accounts, from_date, till_date)
    total = pd.concat([total, total_new_lines]).reset_index(drop=True)
    total.to_csv(config.mankkoo_file_path('total'), index=False)
    log.info('Total money data was updated successfully')
    return total

def __drop_from_total_days(total: pd.DataFrame, min_date: datetime.date):
    return total.drop(total[total['Date'] >= min_date].index)

def __calc_totals(accounts: pd.DataFrame, from_date: datetime.date, till_date: datetime.date):
    investments = importer.load_data_from_file(models.FileType.INVESTMENT)
    stock = importer.load_data_from_file(models.FileType.STOCK)

    result_list = []

    # TODO replace with better approach, e.g.
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    date = from_date
    numdays = (till_date - from_date).days + 1
    for i in range(0, numdays):
        total = accounts_balance_for_day(accounts, date) + investments_for_day(investments, date) + stock_for_day(stock, date)
        row_dict = {'Date': date, 'Total': round(total, 2)}
        result_list.append(row_dict)
        date = date + datetime.timedelta(days=1)

    return pd.DataFrame(result_list)

def accounts_balance_for_day(accounts: pd.DataFrame, date: datetime.date):
    account_names = accounts['Account'].unique()

    result = 0
    for account_name in account_names:
        result = result + __get_balance_for_day_or_earlier(accounts, account_name, date)
    return result

def __get_balance_for_day_or_earlier(accounts: pd.DataFrame, account_name: str, date: datetime.date):

    only_single_account = accounts[accounts['Account'] == account_name]
    only_specific_dates_accounts = only_single_account.loc[only_single_account['Date'] <= date]

    if only_specific_dates_accounts.empty:
        return 0
    return only_specific_dates_accounts['Balance'].iloc[-1]

def investments_for_day(investments: pd.DataFrame, date: datetime.date) -> float:
    """Sums all investments in particular day

    Args:
        investments (pd.DataFrame): DataFrame with all operations for investments
        date (datetime.date): a day for which sum of investments need to be calculated

    Returns:
        float: calculated total sum of all investments
    """
    after_start = investments['Start Date'] <= date
    before_end = investments['End Date'] >= date
    is_na = pd.isna(investments['End Date'])

    active_inv = investments.loc[after_start & (before_end | is_na)]
    return active_inv['Start Amount'].to_numpy().sum()

def stock_for_day(stock: pd.DataFrame, date: datetime.date) -> float:
    """Sums all stock data in particular day

    Args:
        stock (pd.DataFrame): DataFrame with all operations with stocks
        date (datetime.date): a day for which sum of stocks need to be calculated

    Returns:
        float: calculated total sum of all stock value
    """
    df = stock.loc[stock['Date'] <= date]
    df['Change'] = [1 if x == 'Buy' else -1 for x in df['Operation']]
    df['Val'] = df['Total Value'] * df['Change']
    return df['Val'].sum()


def last_month_income(total: pd.DataFrame, date: datetime.date) -> float:
    """Calculate income from previous month.
    Compares latest total in previous month with lastest total in month before.

    Args:
        total (pd.DataFrame): historical data of total money
        date (datetime.date): date for which income will be calculated, usually today

    Returns:
        float: result of comparing two totals from previous months
    """

    temp = total
    temp['Date'] = pd.to_datetime(temp['Date'])
    temp = temp.set_index('Date')

    month_1 = date - relativedelta(months=1)
    month_1_str = month_1.strftime('%b-%Y')
    month_2 = date - relativedelta(months=2)
    month_2_str = month_2.strftime('%b-%Y')

    month_1_data = temp.loc[month_1_str]
    month_2_data = temp.loc[month_2_str]

    month_1_data = month_1_data.sort_index()
    month_2_data = month_2_data.sort_index()
    
    if (month_1_data.empty):
        month_1_total = 0
    else:
        month_1_total = month_1_data['Total'].iloc[-1]

    if (month_2_data.empty):
        month_2_total = 0
    else:
        month_2_total = month_2_data['Total'].iloc[-1]

    return month_1_total - month_2_total
