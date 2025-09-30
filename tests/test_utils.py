from datetime import date, datetime, time
from src.spacextracker.services import utils


def test_to_datetime_start_of_day():
    d = date(2025, 9, 30)
    dt = utils.to_datetime(d)
    assert dt == datetime(2025, 9, 30, 0, 0, 0)


def test_to_datetime_end_of_day():
    d = date(2025, 9, 30)
    dt = utils.to_datetime(d, end=True)
    # time.max = 23:59:59.999999
    assert dt == datetime.combine(d, time.max)
