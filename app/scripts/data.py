from enum import Enum
import app.scripts.importer as importer
import pandas as pd
import numpy as np

class Bank(Enum):
    PL_MBANK = 'pl_mbank'
    PL_MILLENIUM = 'pl_millenium'

account_file = 'account.csv'

def add_new_operations(bank: Bank, file_name: str):
    
    if bank == Bank.PL_MILLENIUM:
        df_new = importer.load_pl_millenium(file_name)
    else:
        raise KeyError("Failed to load data from file. Not known bank. Was provided {} bank".format(bank))
    
    df = importer.load_data(account_file)
    df = pd.concat([df, df_new]).reset_index(drop=True)

    return calculate_balance(df)
    
def calculate_balance(df: pd.DataFrame):

    nan_index = df['Balance'].index[df['Balance'].apply(np.isnan)]

    for i in range(nan_index[0], len(df)):
        df.loc[i, 'Balance'] = df.loc[i-1, 'Balance'] + df.loc[i, 'Operation']
    
    return df