import io
import numpy as np
import pandas as pd
import mankkoo.account.models as models
import mankkoo.database as db


class Ing(models.Importer):
    # ING bank (PL) - https://www.ing.pl

    def load_file_by_filename(self, file_path: str):
        return pd.read_csv(file_path, sep=";")

    def load_file_by_contents(self, contents):
        return pd.read_csv(io.StringIO(contents.decode('utf-8')), sep=";")

    def format_file(self, df: pd.DataFrame, account_id: str):
        df = self.__clean_data(df)

        df = df[[
            'Data transakcji',
            'Dane kontrahenta',
            'Kwota transakcji (waluta rachunku)',
            'Waluta']]

        df = df.loc[:, ~df.columns.duplicated()]

        df = df.rename(columns={
            'Data transakcji': 'Date',
            'Dane kontrahenta': 'Title',
            'Kwota transakcji (waluta rachunku)': 'Operation',
            'Waluta': 'Currency'})

        df['Date'] = pd.to_datetime(df.Date)
        df['Date'] = df['Date'].dt.date
        df['Account'] = account_id
        df['Account'] = df['Account'].astype('string')
        df['Details'] = np.NaN
        df['Balance'] = np.NaN

        df['Operation'] = df['Operation'].str.replace(',', '.')
        df['Operation'] = pd.to_numeric(df['Operation'])

        result = self.__add_missing_columns(df, ['Category', 'Comment'])
        result = result.sort_values(by="Date")
        result.reset_index(drop=True, inplace=True)
        result = result[db.account_columns]
        return result

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
