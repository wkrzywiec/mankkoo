import numpy as np
import pandas as pd
import io
import mankkoo.account.models as models
import mankkoo.database as db


class Millenium(models.Importer):
    # Millenium bank (PL) - https://www.bankmillennium.pl

    def load_file_by_filename(self, file_path: str):
        return pd.read_csv(file_path)

    def load_file_by_contents(self, contents: str):
        return pd.read_csv(io.StringIO(contents.decode('utf-8')))

    def format_file(self, df: pd.DataFrame, account_id: str):
        df = df[['Data transakcji', 'Opis', 'Obciążenia', 'Uznania', 'Waluta']]

        df['Operation'] = np.where(df['Obciążenia'] < 0, df['Obciążenia'], df['Uznania'])
        df = df.drop(columns=['Obciążenia', 'Uznania'])

        df = df.rename(columns={'Data transakcji': 'Date', 'Opis': 'Title', 'Waluta': 'Currency'})

        df['Date'] = pd.to_datetime(df.Date)
        df['Date'] = df['Date'].dt.date
        df['Account'] = account_id
        df['Account'] = df['Account'].astype('string')
        df['Details'] = np.NaN
        df['Balance'] = np.NaN

        result = self.__add_missing_columns(df, ['Category', 'Comment'])
        result = result.iloc[::-1]
        result = result[db.account_columns]
        return result

    def __add_missing_columns(self, df: pd.DataFrame, columns):
        existing_columns = list(df.columns)
        return df.reindex(columns=existing_columns + columns)
