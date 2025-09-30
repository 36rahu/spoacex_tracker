from datetime import datetime, time, date


def to_datetime(d: date, end: bool = False) -> datetime:
    """
    Convert a date to a datetime at the start or end of the day.

    Args:
        d (date): The date to convert.
        end (bool): If True, set time to 23:59:59.999999; otherwise 00:00:00.

    Returns:
        datetime: Datetime corresponding to start or end of the given date.
    """
    if end:
        return datetime.combine(d, time.max)
    return datetime.combine(d, time.min)
