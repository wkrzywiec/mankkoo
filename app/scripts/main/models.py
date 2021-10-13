from enum import Enum
from abc import ABC, abstractmethod
import pandas as pd

class Importer(ABC):
    """Parent class for every bank account importer, which takes care for transforming bank specific format into Mankkoo's
    """

    @abstractmethod
    def load_file_by_filename(self, file_name: str) -> pd.DataFrame:
        """Load bank specific account history file located in /data folder into Pandas DataFrame

        Args:
            file_name (str): name of a file

        Returns:
            pd.DataFrame: raw, unformatted Pandas Dataframe
        """
        pass

    @abstractmethod
    def load_file_by_contents(self, contents: str) -> pd.DataFrame:
        """Load bank specific account history from 64base encoded string, provided from UI

        Args:
            contents (str): base64 encoded string

        Returns:
            pd.DataFrame: raw, unformatted Pandas Dataframe
        """
        pass

    @abstractmethod
    def format_file(self, df: pd.DataFrame, account_name=None) -> pd.DataFrame:
        """Transforms raw bank specific account history data into Mankkoo's format

        Args:
            df (pd.DataFrame): raw, unformatted account history
            account_name ([type], optional): Name of a bank account. Defaults to None.

        Returns:
            pd.DataFrame: formatted DataFrame
        """
        pass

class FileType(Enum):
    """Representation of file type supported in Mankkoo

    Args:
        Enum ([type]): name
    """
    ACCOUNT = 'account'
    INVESTMENT = 'investment'
    STOCK = 'stock'
    TOTAL = 'total'
    BANK = 'bank'

class Bank(Enum):
    """Representations of supported bank reports exports. Special value is MANKKOO, which is used to load a file in mankkoo format

    Args:
        Enum (str): country code (ISO-3166) and name of a bank
    """
    MANKKOO = 'MANKKOO'
    PL_MBANK = 'PL_MBANK'
    PL_MILLENIUM = 'PL_MILLENIUM'
    PL_ING = 'PL_ING'

class Account(Enum):
    """Representations of different kinds of account, like checking, savings, cash or for retirement

    Args:
        Enum (str): string name of a type
    """
    CHECKING = 'checking'
    SAVINGS = 'savings'
    RETIREMENT = 'retirement'
    CASH = 'cash'
