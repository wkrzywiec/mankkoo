import pandas as pd
import numpy as np
from sys import platform
import base64
import io
import scripts.main.config as config
import scripts.main.models as models
import scripts.main.importer.pl as pl_importer
from scripts.main.base_logger import log


def load_total() -> pd.DataFrame:
    log.info('Loading TOTAL file')

    result = pd.read_csv(config.mankkoo_file_path('total'), parse_dates=['Date'])
    result = result.astype({'Date': 'datetime64[ns]', 'Total': 'float'})
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