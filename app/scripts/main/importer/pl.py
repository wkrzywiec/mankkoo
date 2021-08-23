import numpy as np
import pandas as pd
import os
import scripts.main.models as models
import scripts.main.config as config

class Millenium(models.Importer):
    # Millenium bank (PL) - https://www.bankmillennium.pl

    def load_file(self, file_name: str, account_name=None):
        df = self.__read_from_data_path(file_name)
        df = df[['Data transakcji', 'Opis', 'Obciążenia', 'Uznania', 'Waluta']]

        df['Operation'] = np.where(df['Obciążenia'] < 0, df['Obciążenia'], df['Uznania'])
        df = df.drop(columns=['Obciążenia', 'Uznania'])

        df = df.rename(columns={'Data transakcji': 'Date', 'Opis': 'Title', 'Waluta': 'Currency'})

        df['Date'] = pd.to_datetime(df.Date)
        df['Bank'] = 'Millenium'
        df['Type'] = models.Account.CHECKING.value
        df['Account'] = account_name if account_name is not None else 'Millenium Account'
        df['Bank'] = df['Bank'].astype('string')
        result = self.__add_missing_columns(df, ['Category', 'Comment'])
        result = result.sort_values(by="Date")
        return result

    def __read_from_data_path(self, file_name: str):
        return pd.read_csv(config.data_path() + file_name)

    def __add_missing_columns(self, df: pd.DataFrame, columns):
        existing_columns = list(df.columns)
        return df.reindex(columns=existing_columns + columns)

class Ing(models.Importer):
    # ING bank (PL) - https://www.ing.pl

    def load_file(self, file_name: str, account_name=None):
        temp_file_path = self.__prepare_temp_file(file_name)
        df = self.__read_from_data_path(temp_file_path)

        df = df[['Data transakcji', 'Tytu�', 'Kwota transakcji (waluta rachunku)', 'Waluta']]
        df = df.rename(columns={
            'Data transakcji': 'Date',
            'Tytu�': 'Title',
            'Kwota transakcji (waluta rachunku)': 'Operation',
            'Waluta': 'Currency'})

        df['Date'] = pd.to_datetime(df.Date)
        df['Bank'] = 'ING'
        df['Type'] = models.Account.CHECKING.value
        df['Account'] = account_name if account_name is not None else 'ING Account'
        df['Bank'] = df['Bank'].astype('string')
        result = self.__add_missing_columns(df, ['Category', 'Comment'])
        result = result.sort_values(by="Date")
        result.reset_index(drop=True, inplace=True)
        os.remove(temp_file_path)
        return result

    def __prepare_temp_file(self, file_name: str):
        temp_content = self.__clean_data(file_name)
        return self.__save_file(file_name, temp_content)

    def __clean_data(self, file_name: str):
        with open(config.data_path() + file_name, 'r+') as file:
            lines = file.readlines()
            file.close()

            start_index = 0
            stop_index = 0

            for i, elem in enumerate(lines):
                if 'Data transakcji' in elem and start_index == 0:
                    start_index = i

                if start_index != 0 and elem.strip() == '':
                    stop_index = i
                    break

        return lines[start_index:stop_index]

    def __save_file(self, file_name: str, temp_content):
        temp_file_path = config.data_path() + file_name + '_temp'
        temp_file = open(temp_file_path, 'w')

        for line in temp_content:
            temp_file.write(line)

        temp_file.close()
        return temp_file_path

    def __read_from_data_path(self, file_name: str):
        return pd.read_csv(file_name, sep=';')

    def __add_missing_columns(self, df: pd.DataFrame, columns):
        existing_columns = list(df.columns)
        return df.reindex(columns=existing_columns + columns)
