import datetime

def date(date: str):
    return datetime.datetime.strptime(date, "%d-%m-%Y").date()