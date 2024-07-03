import inspect
from abc import ABC, abstractmethod
# pylint: disable=unused-import
from datetime import datetime, timedelta
from dateutil.rrule import rrule, MONTHLY, DAILY, YEARLY
import time
# pylint: disable=unused-import
from dateutil.relativedelta import relativedelta
from tqdm import tqdm


class DatePart(ABC):
    """
    Abstract base class for defining date parts.

    Attributes:
        None

    Methods:
        get_selector: Returns the date selector type (e.g., DAILY, MONTHLY, YEARLY).
        get_arg: Returns the string representation of the date part (e.g., "days", "months", "years").
    """
    @abstractmethod
    def get_selector(self):
        """
        Abstract method to be implemented by subclasses.
        Returns the date selector type.
        """
        pass

    @abstractmethod
    def get_arg(self):
        """
        Abstract method to be implemented by subclasses.
        Returns the string representation of the date part.
        """
        pass


class Day(DatePart):
    """
    Represents a day as a date part.

    Attributes:
        None

    Methods:
        get_selector: Returns DAILY as the date selector type.
        get_arg: Returns "days" as the string representation of the date part.
    """

    def get_selector(self):
        """
        Returns the date selector type for daily frequency.
        """
        return DAILY

    def get_arg(self):
        """
        Returns the string representation of the date part for days.
        """
        return "days"


class Month(DatePart):
    """
    Represents a month as a date part.

    Attributes:
        None

    Methods:
        get_selector: Returns MONTHLY as the date selector type.
        get_arg: Returns "months" as the string representation of the date part.
    """

    def get_selector(self):
        """
        Returns the date selector type for monthly frequency.
        """
        return MONTHLY

    def get_arg(self):
        """
        Returns the string representation of the date part for months.
        """
        return "months"


class Year(DatePart):
    """
    Represents a year as a date part.

    Attributes:
        None

    Methods:
        get_selector: Returns YEARLY as the date selector type.
        get_arg: Returns "years" as the string representation of the date part.
    """

    def get_selector(self):
        """
        Returns the date selector type for yearly frequency.
        """
        return YEARLY

    def get_arg(self):
        """
        Returns the string representation of the date part for years.
        """
        return "years"


def dateLoop(start_date, end_date, date_part: DatePart, fn=lambda start, end: None, *args, **kwargs):
    """
    Executes a loop over a date range based on the provided date part.

    Args:
        start_date (datetime): The start date of the range.
        end_date (datetime): The end date of the range.
        date_part (DatePart): An instance of DatePart specifying the granularity of the loop (days, months, or years).
        fn (callable, optional): A function to be called for each iteration of the loop.
        *args: Variable length argument list passed to the function.
        **kwargs: Arbitrary keyword arguments passed to the function.

    Returns:
        None

    Raises:
        ValueError: If an invalid time unit is specified in date_part.
    """

    fn_args = list(inspect.signature(fn).parameters)

    if date_part.get_arg() == 'days':
        total_iterations = (end_date - start_date).days
    elif date_part.get_arg() == 'months':
        total_iterations = (end_date.year - start_date.year) * \
            12 + (end_date.month - start_date.month)
    elif date_part.get_arg() == 'years':
        total_iterations = end_date.year - start_date.year
    else:
        raise ValueError('Invalid time unit specified')

    max_requests_per_second = 10
    time_interval = 1 / max_requests_per_second
    previous_time = datetime.now()

    with tqdm(total=total_iterations, desc=f"Downloading reports by {date_part.get_arg()}") as pbar:
        for start in rrule(date_part.get_selector(), dtstart=start_date, until=end_date):
            fn_string = f'end = datetime({start.year}, {start.month}, {start.day}) '\
                f'+ relativedelta({date_part.get_arg()}=1) - relativedelta(days=1)'
            namespace = {}

            # pylint: disable=exec-used
            exec('from datetime import datetime, timedelta', namespace)
            exec('from dateutil.relativedelta import relativedelta', namespace)
            exec(fn_string, namespace)

            end = namespace['end']

            current_time = datetime.now()
            time_diff = (current_time - previous_time).total_seconds()
            if time_diff < time_interval:
                time.sleep(time_interval - time_diff)

            if 'start' in fn_args and 'end' in fn_args:
                fn(start, end, *args, **kwargs)
            else:
                fn(*args, **kwargs)
            pbar.update(1)
