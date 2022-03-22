import datetime
import re

def map_date(date: str) -> datetime.date:
    """Map date in string to date object

    Args:
        date (str): date as a string

    Raises:
        ValueError: raised when unknown date with unsupported date format has been provided

    Returns:
        (date): date object
    """
    pattern = ''

    if __match(date, "\d{1,2}-\d{1,2}-\d{4}"):
        pattern = "%d-%m-%Y"
    elif __match(date, "\d{4}-\d{1,2}-\d{1,2}"):
        pattern = "%Y-%m-%d"
    else:
        raise ValueError("Unsupported date format. Currently only 02-01-2021 and 2021-01-02 are supported")
    
    return datetime.datetime.strptime(date, pattern).date()

def __match(value, regex):
    return bool(re.match(regex, value))