import os
import numpy as np
import pandas as pd
import base64
import io
import scripts.main.models as models
import scripts.main.config as config
import scripts.main.data as data

class Ing(models.Importer):
    # ING bank (PL) - https://www.ing.pl

    def load_file_by_filename(self, file_name: str):
        return pd.read_csv(config.data_path() + file_name, sep=";")

    def load_file_by_contents(self, contents):
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        return pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=";")

    def format_file(self, df: pd.DataFrame, account_name=None):
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


class Mbank(models.Importer):
    # Mbank bank (PL) - https://www.mbank.pl

    def load_file_by_filename(self, file_name: str) -> pd.DataFrame:

        skip_lines = self.__skip_rows_footer(file_name)
        # return pd.read_csv(config.data_path() + file_name, sep=";", skiprows=skip_lines["skiprows"], skipfooter=skip_lines["skipfooter"])
        return pd.read_csv(config.data_path() + file_name, sep=";", skiprows=skip_lines["skiprows"])

    def load_file_by_contents(self, contents: str) -> pd.DataFrame:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        temp_file_path = config.data_path() + 'temp_mbank.csv'
        temp_file = open(temp_file_path, 'w', encoding="utf-8")
        
        decoded_str = decoded.decode("utf-8")
        lines = decoded_str.split("\n")
        non_empty_lines = [line for line in lines if line.strip() != ""]
        cleaned_decoded_content = ""
        for line in non_empty_lines:
            cleaned_decoded_content += line + "\n"
        
        temp_file.write(cleaned_decoded_content)
        temp_file.close()

        result = self.load_file_by_filename('temp_mbank.csv')
        os.remove(temp_file_path)

        return result

    def __skip_rows_footer(self, file_name: str):
        skiprows = 0
        skipfooter = 0
        lines = 0
        for row in open(config.data_path() + file_name):
            if '#Data operacji' in row:
                skiprows = lines
            if '#Saldo' in row:
                skipfooter = lines
            lines += 1
        return {
            "skiprows": skiprows,
            "skipfooter": lines - skipfooter
        }

    def format_file(self, df: pd.DataFrame, account_name=None):

        df = df[['#Data operacji', '#Kategoria']]

        df = df.loc[:, ~df.columns.duplicated()]

        df = df.rename(columns={
            '#Data operacji': 'Title',
            '#Kategoria': 'Operation'})
        df['Operation'] = df['Operation'].str.replace(r'PLN', '')
        df['Date'] = df.index

        df['Date'] = pd.to_datetime(df.Date)
        df['Date'] = df['Date'].dt.date
        df['Bank'] = 'Mbank'
        df['Bank'] = df['Bank'].astype('string')
        df['Type'] = models.Account.CHECKING.value
        df['Account'] = account_name if account_name is not None else 'Mbank Account'
        df['Account'] = df['Account'].astype('string')
        df['Currency'] = 'PLN'
        df['Details'] = np.NaN
        df['Balance'] = np.NaN

        df['Operation'] = df['Operation'].str.replace(',', '.')
        df['Operation'] = df['Operation'].str.replace(' ', '')
        df['Operation'] = pd.to_numeric(df['Operation'])

        result = self.__add_missing_columns(df, ['Category', 'Comment'])
        result = result.sort_values(by="Date")
        result.reset_index(drop=True, inplace=True)
        result = result[data.account_columns]
        return result

    def __add_missing_columns(self, df: pd.DataFrame, columns):
        existing_columns = list(df.columns)
        return df.reindex(columns=existing_columns + columns)


class Millenium(models.Importer):
    # Millenium bank (PL) - https://www.bankmillennium.pl

    def load_file_by_filename(self, file_name: str):
        return pd.read_csv(config.data_path() + file_name)

    def load_file_by_contents(self, contents: str):
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        return pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    def format_file(self, df: pd.DataFrame, account_name=None):
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
        result = result.iloc[::-1]
        result = result[data.account_columns]
        return result

    def __add_missing_columns(self, df: pd.DataFrame, columns):
        existing_columns = list(df.columns)
        return df.reindex(columns=existing_columns + columns)
