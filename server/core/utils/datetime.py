import datetime


def utcnow() -> datetime:
    """
    Returns the current time in UTC but with tzinfo set, as opposed
    to datetime.utcnow which does not.
    """
    return datetime.datetime.now(datetime.timezone.utc)
