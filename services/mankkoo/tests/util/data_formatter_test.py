import datetime

import pytest

import mankkoo.util.data_formatter as formatter


@pytest.mark.parametrize("date_string", ["02-01-2021", "2021-01-02"])
def test_format_date(date_string):

    # WHEN
    mapped_date = formatter.map_date(date_string)

    # THEN
    assert mapped_date == datetime.date(2021, 1, 2)
