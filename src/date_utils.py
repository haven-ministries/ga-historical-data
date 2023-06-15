from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from dateutil.rrule import rrule, MONTHLY, DAILY, YEARLY
from dateutil.relativedelta import relativedelta
import inspect
from tqdm import tqdm


class DatePart(ABC):
    @abstractmethod
    def getSelector(self):
        pass

    @abstractmethod
    def getArg(self):
        pass


class Day(DatePart):
    def getSelector(self):
        return DAILY

    def getArg(self):
        return "days"


class Month(DatePart):
    def getSelector(self):
        return MONTHLY

    def getArg(self):
        return "months"


class Year(DatePart):
    def getSelector(self):
        return YEARLY

    def getArg(self):
        return "years"


def dateLoop(start_date, end_date, date_part: DatePart, fn=lambda start, end: None, *args, **kwargs):

    fn_args = list(inspect.signature(fn).parameters)

    if date_part.getArg() == 'days':
        total_iterations = (end_date - start_date).days
    elif date_part.getArg() == 'months':
        total_iterations = (end_date.year - start_date.year) * \
            12 + (end_date.month - start_date.month)
    elif date_part.getArg() == 'years':
        total_iterations = end_date.year - start_date.year
    else:
        raise ValueError('Invalid time unit specified')

    with tqdm(total=total_iterations, desc=f"Downloading reports by {date_part.getArg()}") as pbar:
        for start in rrule(date_part.getSelector(), dtstart=start_date, until=end_date):
            fn_string = f'end = datetime({start.year}, {start.month}, {start.day}) + relativedelta({date_part.getArg()}=1) - relativedelta(days=1)'
            namespace = {}
            exec('from datetime import datetime, timedelta', namespace)
            exec('from dateutil.relativedelta import relativedelta', namespace)
            exec(fn_string, namespace)

            end = namespace['end']

            if 'start' in fn_args and 'end' in fn_args:
                fn(start, end, *args, **kwargs)
            else:
                fn(*args, **kwargs)
            pbar.update(1)
