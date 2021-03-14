import pytest
import app.scripts.data_formatter as formatter
import datetime

@pytest.mark.parametrize(
    "date_string",
    ['02-01-2021', '2021-01-02'])
def format_date_test(date_string):

    # WHEN
    mapped_date = formatter.map_date(date_string)

    # THEN
    assert mapped_date == datetime.date(2021, 1, 2)
