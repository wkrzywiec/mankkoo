import numpy as np
import pandas as pd
import io
import mankkoo.account.models as models
import mankkoo.database as db


def select_only_required_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df[[
        'Data transakcji',
        'Odbiorca/Zleceniodawca',
        'Opis',
        'Obciążenia',
        'Uznania',
        'Waluta']]
    return df


def get_operation(df: pd.DataFrame) -> pd.DataFrame:
    df['Operation'] = np.where(df['Obciążenia'] < 0, df['Obciążenia'], df['Uznania'])
    return df


def prepare_tile(df: pd.DataFrame) -> pd.DataFrame:
    df['Title'] = df['Odbiorca/Zleceniodawca'] + ' - ' + df['Opis']
    df['Title'] = df['Title'].str.replace(',', '')
    df['Title'] = df['Title'].str.replace(r'\s+', ' ', regex=True)
    df['Title'] = df['Title'].str.strip()
    return df


def remove_unnecessary_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=['Obciążenia', 'Uznania', 'Odbiorca/Zleceniodawca'])
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={'Data transakcji': 'Date', 'Waluta': 'Currency'})
    return df


def format_date_column(df: pd.DataFrame) -> pd.DataFrame:
    df['Date'] = pd.to_datetime(df.Date)
    df['Date'] = df['Date'].dt.date
    return df


def add_account_id_to_each_row(df: pd.DataFrame, account_id: str) -> pd.DataFrame:
    df['Account'] = account_id
    df['Account'] = df['Account'].astype('string')
    return df


def add_details_and_balance_columns(df: pd.DataFrame) -> pd.DataFrame:
    df['Details'] = np.NaN
    df['Balance'] = np.NaN
    return df


def add_empty_columns(df: pd.DataFrame, columns) -> pd.DataFrame:
    existing_columns = list(df.columns)
    return df.reindex(columns=existing_columns + columns)


def reverse_rows_order(df: pd.DataFrame) -> pd.DataFrame:
    return df.iloc[::-1]


def order_columns(
        df: pd.DataFrame,
        columns_in_order: list[str]) -> pd.DataFrame:
    return df[columns_in_order]


class Millenium(models.Importer):
    # Millenium bank (PL) - https://www.bankmillennium.pl

    def load_file_by_filename(self, file_path: str):
        return pd.read_csv(file_path)

    def load_file_by_contents(self, contents: str):
        return pd.read_csv(io.StringIO(contents.decode('utf-8')))

    def format_file(self, df: pd.DataFrame, account_id: str):
        df = df.pipe(select_only_required_columns)\
            .pipe(get_operation)\
            .pipe(prepare_tile)\
            .pipe(remove_unnecessary_columns)\
            .pipe(rename_columns)\
            .pipe(format_date_column)\
            .pipe(add_account_id_to_each_row, account_id)\
            .pipe(add_details_and_balance_columns)\
            .pipe(add_empty_columns, ['Category', 'Comment'])\
            .pipe(reverse_rows_order)\
            .pipe(order_columns, db.account_columns)

        return df
