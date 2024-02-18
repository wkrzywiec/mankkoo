import os
import numpy as np
import pandas as pd
import base64
import mankkoo.account.models as models
import mankkoo.database as db
import mankkoo.util.config as config


class Mbank(models.Importer):
    # Mbank bank (PL) - https://www.mbank.pl
    def load_file_by_filename(self, file_path: str) -> pd.DataFrame:

        skip_lines = self.__skip_rows_footer(file_path)

        return pd.read_csv(file_path, sep=";", skiprows=skip_lines["skiprows"])

    def load_file_by_contents(self, contents: str) -> pd.DataFrame:
        raise Exception('Loading file by its content is not supported!')
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

    def __skip_rows_footer(self, file_path: str):
        skiprows = 0
        skipfooter = 0
        lines = 0
        for row in open(file_path):
            if '#Data operacji' in row:
                skiprows = lines
            if '#Saldo' in row:
                skipfooter = lines
            lines += 1
        return {
            "skiprows": skiprows,
            "skipfooter": lines - skipfooter
        }

    def format_file(self, df: pd.DataFrame, account_id: str):

        df = df[['#Data operacji', '#Kategoria']]
        df = df.loc[:, ~df.columns.duplicated()]

        df = df.rename(columns={
            '#Data operacji': 'Title',
            '#Kategoria': 'Operation'})
        df['Operation'] = df['Operation'].str.replace(r'PLN', '')
        df['Date'] = df.index

        df['Date'] = pd.to_datetime(df.Date)
        df['Date'] = df['Date'].dt.date
        df['Account'] = account_id
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
        result = result[db.account_columns]
        return result

    def __add_missing_columns(self, df: pd.DataFrame, columns):
        existing_columns = list(df.columns)
        return df.reindex(columns=existing_columns + columns)
