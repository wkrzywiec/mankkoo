import pytest
import app.scripts.data as data
import datetime

def date_test():
    date_string = '02-01-2021'
    assert data.date(date_string) == datetime.date(2021, 1, 2)
