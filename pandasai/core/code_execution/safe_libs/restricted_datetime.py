import datetime

from .base_restricted_module import BaseRestrictedModule


class RestrictedDatetime(BaseRestrictedModule):
    def __init__(self):
        self.allowed_attributes = [
            # Classes
            "date",
            "time",
            "datetime",
            "timedelta",
            "tzinfo",
            "timezone",
            # Constants
            "MINYEAR",
            "MAXYEAR",
            # Time zone constants
            "UTC",
            # Functions
            "now",
            "utcnow",
            "today",
            "fromtimestamp",
            "utcfromtimestamp",
            "fromordinal",
            "combine",
            "strptime",
            # Timedelta operations
            "timedelta",
            # Date operations
            "weekday",
            "isoweekday",
            "isocalendar",
            "isoformat",
            "ctime",
            "strftime",
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "microsecond",
            # Time operations
            "replace",
            "tzname",
            "dst",
            "utcoffset",
            # Comparison methods
            "min",
            "max",
        ]

        for attr in self.allowed_attributes:
            if hasattr(datetime, attr):
                setattr(self, attr, self._wrap_function(getattr(datetime, attr)))

    def __getattr__(self, name):
        if name not in self.allowed_attributes:
            raise AttributeError(f"'{name}' is not allowed in RestrictedDatetime")

        return getattr(datetime, name)
