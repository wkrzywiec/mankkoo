from enum import Enum
from abc import ABC, abstractmethod
import pandas as pd

class Importer(ABC):

    @abstractmethod
    def load_file_by_filename(self, file_name: str):
        pass

    @abstractmethod
    def load_file_by_contents(self, contents):
        pass

    @abstractmethod
    def format_file(self, df: pd.DataFrame, account_name=None):
        pass

class FileType(Enum):
    ACCOUNT = 'account'
    INVESTMENT = 'investment'
    STOCK = 'stock'
    TOTAL = 'total'
    BANK = 'bank'

class Bank(Enum):
    """Representations of supported bank reports exports. Special value is MANKKOO, which is used to load a file in mankkoo format

    Args:
        Enum (str): country and name of a bank
    """
    MANKKOO = 'mankkoo'
    PL_MBANK = 'pl_mbank'
    PL_MILLENIUM = 'pl_millenium'
    PL_ING = 'pl_ing'

class Account(Enum):
    """Representations of different kinds of account, like checking, savings, cash or for retirement

    Args:
        Enum (str): string name of a type
    """
    CHECKING = 'checking'
    SAVINGS = 'savings'
    RETIREMENT = 'retirement'
    CASH = 'cash'
