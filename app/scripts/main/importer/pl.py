import numpy as np
import pandas as pd
import scripts.main.config as config
import scripts.main.models as models

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
