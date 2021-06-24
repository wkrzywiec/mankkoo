import pandas as pd
import numpy as np
import scripts.main.importer as importer

def total_money_data(data: dict):

    checking_account = __latest_account_balance(data, '360')
    savings_account = __latest_account_balance(data, 'Konto Oszczędnościowe Profit')
    cash = __latest_account_balance(data, 'Gotówka')
    ppk = __latest_account_balance(data, 'PKO PPK')

    inv = data['investment'].loc[data['investment']['Active'] == True]
    inv = inv['Start Amount'].sum()

    stock_buy = data['stock'].loc[data['stock']['Operation'] == 'Buy']
    stock_buy = stock_buy['Total Value'].sum()
    # TODO check how much stock units I have Broker-Title pair buy-sell
    total = checking_account + savings_account + cash + ppk + inv + stock_buy

    return pd.DataFrame([
        {'Type': 'Checking Account', 'Total': checking_account, 'Percentage': checking_account/total},
        {'Type': 'Savings Account', 'Total': savings_account, 'Percentage': savings_account/total},
        {'Type': 'Cash', 'Total': cash, 'Percentage': cash/total},
        {'Type': 'PPK', 'Total': ppk, 'Percentage': ppk/total},
        {'Type': 'Investments', 'Total': inv, 'Percentage': inv/total},
        {'Type': 'Stocks', 'Total': stock_buy, 'Percentage': stock_buy/total}
    ])

def __latest_account_balance(data: dict, type: str) -> float:
    
    #TODO filter by account type, not name, and if more than one sum it
    df = data['account'].loc[data['account']['Account'] == type]
    if not df.empty:
        return df['Balance'].iloc[-1]
    return 0.00

def update_total_money(df: pd.DataFrame, updated_dates: df.Series):
    total = importer.load_data(importer.FileType.TOTAL)

    investment = importer.load_data(importer.FileType.INVESTMENT)
    stock = importer.load_data(importer.FileType.STOCK)
    # TODO two categories - retire and all total money
    

    # wykasuj wszystkie operacje do najpóźniejszego dnia z df
    # dla każdego dnia z serii wykalkuluj total (usuń duplikaty, )
    # dodaj do totala posortowane wyniki
    # zapisz totala
    pass

def total_money_in_time(data: dict):
    # znajdź wszystkie pnkty w czasie, wszystkie unikalne daty
    # iteracja po każdym dniu po 3 dataframeach - account, invest oraz stock i dodanie

    df = data['account']['Date'].drop_duplicates().reset_index(drop=True).to_frame()
    df['Total'] = np.nan

    # TODO replace with better approach, e.g.
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    for index, row in df.iterrows():
        row['Total'] = _calculate_total(data, row['Date'])

def _calculate_total(data: dict, date):
    # pobrać z każdego dnia wartość na koncie, jeśli tylko jedno konto danego dnia - ostatnia wartość i dodać do innych kont z poprzednich dni
    print(date)
