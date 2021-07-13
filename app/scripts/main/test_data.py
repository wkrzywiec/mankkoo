import numpy as np
import pandas as pd
import scripts.main.data as data


def account_data(rows):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=data.account_columns
    ).astype({'Balance': 'float', 'Operation': 'float', 'Date': 'datetime64[ns]'})
    result['Date'] = result['Date'].dt.date
    return result

def investment_data(rows):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=data.invest_columns
    ).astype({'Active': 'int', 'Start Amount': 'float', 'End amount': 'float', 'Start Date': 'datetime64[ns]', 'End Date': 'datetime64[ns]'})
    result['Start Date'] = result['Start Date'].dt.date
    result['End Date'] = result['End Date'].dt.date
    return result

def stock_data(rows):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=data.stock_columns
    ).astype({'Total Value': 'float', 'Date': 'datetime64[ns]'})
    result['Date'] = result['Date'].dt.date
    return result

def total_data(rows):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=data.total_columns
    ).astype({'Date': 'datetime64[ns]', 'Total': 'float'})
    result['Date'] = result['Date'].dt.date
    return result
