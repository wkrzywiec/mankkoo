import pandas as pd
from sys import platform
import scripts.main.config as config
from scripts.main.base_logger import log

log.basicConfig(level=log.DEBUG)

account_columns = ['Account', 'Date', 'Title', 'Details', 'Category', 'Comment', 'Operation', 'Currency', 'Balance']
invest_columns = ['Active', 'Category', 'Bank', 'Investment', 'Start Date', 'End Date', 'Start Amount', 'End amount', 'Currency', 'Details', 'Comment']
stock_columns = ['Broker', 'Date', 'Title', 'Operation', 'Total Value', 'Units', 'Currency', 'Details', 'Url', 'Comment']
total_columns = ['Date', 'Total']
total_monthly_columns = ['Date', 'Income', 'Spending', 'Profit']

def load_all() -> dict:
    """Load aggregated data of all financial data (accounts, investments, etc.)

    Returns:
        dict(pandas.DataFrame): a dictonary with categorized financial data
    """
    log.info("Loading mankkoo's files")

    return dict(
        account=load_accounts(),
        investment=load_investments(),
        stock=load_stocks(),
        total=load_total(),
        total_monthly=load_total_monthly()
    )

def load_total() -> pd.DataFrame:
    log.info('Loading TOTAL file')

    result = pd.read_csv(config.mankkoo_file_path('total'), parse_dates=['Date'])
    result = result.astype({'Date': 'datetime64[ns]', 'Total': 'float'})
    result['Date'] = result['Date'].dt.date
    return result

def load_total_monthly() -> pd.DataFrame:
    log.info('Loading TOTAL MONTHLY file')

    result = pd.read_csv(config.mankkoo_file_path('total_monthly'), parse_dates=['Date'])
    result = result.astype({'Date': 'datetime64[ns]', 'Income': 'float', 'Spending': 'float', 'Profit': 'float'})
    result['Date'] = result['Date'].dt.date
    return result


def load_accounts() -> pd.DataFrame:
    log.info('Loading ACCOUNT file')

    result = pd.read_csv(config.mankkoo_file_path('account'), parse_dates=['Date'], index_col=0)
    result = result.astype({'Account': 'string', 'Balance': 'float', 'Operation': 'float', 'Date': 'datetime64[ns]'})
    result['Date'] = result['Date'].dt.date
    return result

def load_investments() -> pd.DataFrame:
    log.info('Loading INVESTMENT file')

    result = pd.read_csv(config.mankkoo_file_path('investment'), parse_dates=['Start Date', 'End Date'])
    result = result.astype({'Active': 'int', 'Start Amount': 'float', 'End amount': 'float', 'Start Date': 'datetime64[ns]', 'End Date': 'datetime64[ns]'})
    result.Active = result.Active.astype('bool')
    result['Start Date'] = result['Start Date'].dt.date
    result['End Date'] = result['End Date'].dt.date
    return result

def load_stocks() -> pd.DataFrame:
    log.info('Loading STOCK file')

    result = pd.read_csv(config.mankkoo_file_path('stock'), parse_dates=['Date'])
    result = result.astype({'Total Value': 'float', 'Date': 'datetime64[ns]'})
    result['Date'] = result['Date'].dt.date
    return result