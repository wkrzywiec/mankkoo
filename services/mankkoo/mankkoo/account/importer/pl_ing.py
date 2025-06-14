import io

import numpy as np
import pandas as pd

import mankkoo.account.models as models
import mankkoo.database as db


def remove_non_tabular_data(df: pd.DataFrame) -> pd.DataFrame:
    # remove first rows without data
    column = df.iloc[:, 0]
    start_row_index = column.index[column == "Data transakcji"].item()
    df = df.iloc[start_row_index:, :]

    #  remove last row
    df = df[:-1]

    # make first row a header
    df.columns = df.iloc[0]
    df = df[1:]

    # drop columns with header with nan name
    df = df.loc[:, df.columns.notnull()]
    return df.reset_index(drop=True)


def prepare_tile(df: pd.DataFrame) -> pd.DataFrame:
    df["Title"] = df["Dane kontrahenta"] + " - " + df["Tytuł"]
    df["Title"] = df["Title"].str.replace(",", "")
    df["Title"] = df["Title"].str.replace(r"\s+", " ", regex=True)
    df["Title"] = df["Title"].str.strip()
    return df


def select_only_required_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
        [
            "Data transakcji",
            "Title",
            "Kwota transakcji (waluta rachunku)",
            "Waluta",
            "Kwota blokady/zwolnienie blokady",
        ]
    ]
    return df


def remove_duplicated_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.loc[:, ~df.columns.duplicated()]
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"Data transakcji": "Date", "Waluta": "Currency"})
    return df


def format_date_column(df: pd.DataFrame) -> pd.DataFrame:
    df["Date"] = pd.to_datetime(df.Date)
    df["Date"] = df["Date"].dt.date
    return df


def get_operation(df: pd.DataFrame) -> pd.DataFrame:
    df["Operation"] = np.where(
        df["Kwota transakcji (waluta rachunku)"].isna(),
        df["Kwota blokady/zwolnienie blokady"],
        df["Kwota transakcji (waluta rachunku)"],
    )
    df["Operation"] = df["Operation"].str.replace(",", ".")
    df["Operation"] = pd.to_numeric(df["Operation"])
    return df


def remove_unnecessary_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(
        columns=[
            "Kwota transakcji (waluta rachunku)",
            "Kwota blokady/zwolnienie blokady",
        ]
    )
    return df


def add_account_id_to_each_row(df: pd.DataFrame, account_id: str) -> pd.DataFrame:
    df["Account"] = account_id
    df["Account"] = df["Account"].astype("string")
    return df


def add_details_and_balance_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["Details"] = np.NaN
    df["Balance"] = np.NaN
    return df


def add_empty_columns(df: pd.DataFrame, columns) -> pd.DataFrame:
    existing_columns = list(df.columns)
    return df.reindex(columns=existing_columns + columns)


def add_pln_currency_if_empty(df: pd.DataFrame) -> pd.DataFrame:
    df["Currency"] = df["Currency"].fillna("PLN")
    return df


def sort_rows_by_date(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(by="Date")


def reset_row_indexes(df: pd.DataFrame) -> pd.DataFrame:
    df.reset_index(drop=True, inplace=True)
    return df


def order_columns(df: pd.DataFrame, columns_in_order: list[str]) -> pd.DataFrame:
    return df[columns_in_order]


class Ing(models.Importer):
    # ING bank (PL) - https://www.ing.pl

    def load_file_by_filename(self, file_path: str):
        return pd.read_csv(file_path, sep=";")

    def load_file_by_contents(self, contents: bytes):
        return pd.read_csv(io.StringIO(contents.decode("windows-1250")), sep=";")

    def format_file(self, df: pd.DataFrame, account_id: str):
        return (
            df.pipe(remove_non_tabular_data)
            .pipe(prepare_tile)
            .pipe(select_only_required_columns)
            .pipe(remove_duplicated_columns)
            .pipe(rename_columns)
            .pipe(format_date_column)
            .pipe(get_operation)
            .pipe(remove_unnecessary_columns)
            .pipe(add_account_id_to_each_row, account_id)
            .pipe(add_details_and_balance_columns)
            .pipe(add_empty_columns, ["Category", "Comment"])
            .pipe(add_pln_currency_if_empty)
            .pipe(sort_rows_by_date)
            .pipe(reset_row_indexes)
            .pipe(order_columns, db.account_columns)
        )
