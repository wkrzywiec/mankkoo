import numpy as np
import pandas as pd
import os
import scripts.main.models as models
import scripts.main.config as config
import scripts.main.data as data

class Millenium(models.Importer):
    # Millenium bank (PL) - https://www.bankmillennium.pl

    def import_file(self, file_name: str, account_name=None):
        df = self.__read_from_data_path(file_name)
        df = df[['Data transakcji', 'Opis', 'Obciążenia', 'Uznania', 'Waluta']]

        df['Operation'] = np.where(df['Obciążenia'] < 0, df['Obciążenia'], df['Uznania'])
        df = df.drop(columns=['Obciążenia', 'Uznania'])

        df = df.rename(columns={'Data transakcji': 'Date', 'Opis': 'Title', 'Waluta': 'Currency'})

        df['Date'] = pd.to_datetime(df.Date)
        df['Date'] = df['Date'].dt.date
        df['Bank'] = 'Millenium'
        df['Bank'] = df['Bank'].astype('string')

        df['Type'] = models.Account.CHECKING.value
        df['Account'] = account_name if account_name is not None else 'Millenium Account'
        df['Account'] = df['Account'].astype('string')
        df['Details'] = np.NaN
        df['Balance'] = np.NaN

        result = self.__add_missing_columns(df, ['Category', 'Comment'])
        result = result.sort_values(by="Date")
        result = result[data.account_columns]
        return result

    def __read_from_data_path(self, file_name: str):
        return pd.read_csv(config.data_path() + file_name)

    def __add_missing_columns(self, df: pd.DataFrame, columns):
        existing_columns = list(df.columns)
        return df.reindex(columns=existing_columns + columns)

class Ing(models.Importer):
    # ING bank (PL) - https://www.ing.pl

    def import_file(self, file_name: str, account_name=None):
        df = self.__read_from_data_path(file_name)
        df = self.__clean_data(df)

        df = df[['Data transakcji', 'Dane kontrahenta', 'Kwota transakcji (waluta rachunku)', 'Waluta']]

        df = df.loc[:, ~df.columns.duplicated()]

        df = df.rename(columns={
            'Data transakcji': 'Date',
            'Dane kontrahenta': 'Title',
            'Kwota transakcji (waluta rachunku)': 'Operation',
            'Waluta': 'Currency'})

        df['Date'] = pd.to_datetime(df.Date)
        df['Date'] = df['Date'].dt.date
        df['Bank'] = 'ING'
        df['Bank'] = df['Bank'].astype('string')
        df['Type'] = models.Account.CHECKING.value
        df['Account'] = account_name if account_name is not None else 'ING Account'
        df['Account'] = df['Account'].astype('string')
        df['Details'] = np.NaN
        df['Balance'] = np.NaN

        df['Operation'] = df['Operation'].str.replace(',', '.')
        df['Operation'] = pd.to_numeric(df['Operation'])

        result = self.__add_missing_columns(df, ['Category', 'Comment'])
        result = result.sort_values(by="Date")
        result.reset_index(drop=True, inplace=True)
        result = result[data.account_columns]
        return result

    def __read_from_data_path(self, file_name: str):
        return pd.read_csv(config.data_path() + file_name, sep=';')

    def __clean_data(self, df: pd.DataFrame):
        # remove first rows without data
        column = df.iloc[:, 0]
        start_row_index = column.index[column == 'Data transakcji'].item()
        df = df.iloc[start_row_index:, :]

        #  remove last row
        df = df[:-1]

        # make first row a header
        df.columns = df.iloc[0]
        df = df[1:]

        # drop columns with header with nan name
        df = df.loc[:, df.columns.notnull()]
        return df.reset_index(drop=True)

    def __add_missing_columns(self, df: pd.DataFrame, columns):
        existing_columns = list(df.columns)
        return df.reindex(columns=existing_columns + columns)
