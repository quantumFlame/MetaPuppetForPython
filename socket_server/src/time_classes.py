from datetime import datetime, timedelta
import pytz
import re

# init _CUSTOM_TIMEZONE, including all common timezone
# key are all lower case
CUSTOM_TIMEZONE = {'pt': 'US/Pacific',
                    'los angeles': 'US/Pacific',
                    'et': 'US/Eastern',
                    'ct': 'US/Central',
                    'chicago': 'US/Central',
                    'mt': 'US/Mountain', 
                    'beijing': 'Asia/Shanghai',
                    'shanghai': 'Asia/Shanghai',
                    'china': 'Asia/Shanghai',
                    'utc+8': 'Asia/Shanghai',
                    'germany': 'Europe/Berlin',
                    'berlin': 'Europe/Berlin',
                    'paris': 'Europe/Paris',
                    'england': 'Europe/Paris',
                    'uk': 'Europe/Paris',
                    }

for tmp_timezone in pytz.common_timezones:
    CUSTOM_TIMEZONE[tmp_timezone.lower()] = tmp_timezone


class Time(object):
    """docstring for Time"""
    # everyday for 7 days
    # every 2 days for 30 days
    _PATTERN_PERIOD_0 = re.compile('everyday +for +([0-9]+) +day.*')
    _PATTERN_PERIOD_1 = re.compile('every +([0-9]+) +days? +for +([0-9]+) +day.*')

    def __init__(self, text=None, timezone='UTC'):
        super(Time, self).__init__()
        # store local time and timezone
        self.year = None
        self.month = None
        self.day = None
        self.hour = None
        self.minute = None
        self.second = None
        self.timezone = None

        self._PATTERN_TIME_0 = re.compile('^([0-9]{1,4})-([0-9]{1,2})-([0-9]{1,2})-([0-9]{1,2})-([0-9]{1,2})-([0-9]{1,2})$')
        self._PATTERN_TIME_1 = re.compile('^([0-9\-]+) +([0-9:：]+)$')
        self._PATTERN_TIME_YMD_0 = re.compile('^([0-9]{1,4})-([0-9]{1,2})-([0-9]{1,2})$')
        self._PATTERN_TIME_YMD_1 = re.compile('^([0-9]{1,2})-([0-9]{1,2})$')
        self._PATTERN_TIME_HMS_0 = re.compile('^([0-9]{1,2})[:：]([0-9]{1,2})[:：]([0-9]{1,2})$')
        self._PATTERN_TIME_HMS_1 = re.compile('^([0-9]{1,2})[:：]([0-9]{1,2})$')

        if text != None:
            result = self.set_time(text, timezone)
        else:
            result = self.set_time('now', timezone)
        if result == False:
            print('Error! ', text, ' cannot be initialized as time!')

    def __str__(self):
        """ 
            override to str method 
            return local time
        """

        return '{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}'.format(\
            year=self.year, month=self.month, day=self.day, \
            hour=self.hour, minute=self.minute, second=self.second)

    def set_time(self, text, timezone='UTC'):
        """set time according to plain text"""
        self.timezone = Time.parse_timezone(timezone)
        ref_time = None
        if isinstance(text, datetime):
            ref_time = text
        else:
            text = text.strip().lower()
            input_text = text.lower()
            ref_time = self._parse_time(input_text)
        if ref_time != None:
            self.year = ref_time.year
            self.month = ref_time.month
            self.day = ref_time.day
            self.hour = ref_time.hour
            self.minute = ref_time.minute
            self.second = ref_time.second
            return True
        else:
            return False

    def to_timezone(self, timezone):
        tz = pytz.timezone(Time.parse_timezone(timezone))
        datetime_obj = self.to_datetime_obj()
        datetime_obj = datetime_obj.astimezone(tz)
        return Time(datetime_obj.strftime("%Y-%m-%d %H:%M:%S"), timezone=timezone)

    def to_UTC_time(self):
        return self.to_timezone('UTC')

    def to_datetime_obj(self):
        tz = pytz.timezone(self.timezone)
        return tz.localize(datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)) 

    def _parse_time(self, text):
        time_parsed = None
        time_parsed = self._parse_num_time(text)
        if time_parsed != None:
            return time_parsed
        time_parsed = self._parse_text_time(text)
        if time_parsed != None:
            return time_parsed
        return time_parsed

    def _parse_ymd_time(self, text):
        time_parsed = None
        
        tmp_m = self._PATTERN_TIME_YMD_0.match(text)
        if tmp_m:
            time_parsed = datetime(int(tmp_m.group(1)), int(tmp_m.group(2)), int(tmp_m.group(3)),\
                                    23, 59, 59)
            return time_parsed
        tmp_m = self._PATTERN_TIME_YMD_1.match(text)
        if tmp_m:
            tz = pytz.timezone(self.timezone)
            current_time = datetime.now(tz)
            time_parsed = datetime(current_time.year, int(tmp_m.group(1)), int(tmp_m.group(2)), \
                                    23, 59, 59)
            return time_parsed
        return time_parsed

    def _parse_hms_time(self, text):
        time_parsed = None

        tz = pytz.timezone(self.timezone)
        current_time = datetime.now(tz)
        tmp_m = self._PATTERN_TIME_HMS_0.match(text)
        if tmp_m:
            time_parsed = datetime(current_time.year, current_time.month, current_time.day, \
                                    int(tmp_m.group(1)), int(tmp_m.group(2)), int(tmp_m.group(3)))
            return time_parsed
        tmp_m = self._PATTERN_TIME_HMS_1.match(text)
        if tmp_m:
            time_parsed = datetime(current_time.year, current_time.month, current_time.day, \
                                    int(tmp_m.group(1)), int(tmp_m.group(2)), 0)
            return time_parsed
        return time_parsed

    def _parse_num_time(self, text):
        time_parsed = None
        
        tmp_m = self._PATTERN_TIME_0.match(text)
        if tmp_m:
            time_parsed = datetime(int(tmp_m.group(1)), int(tmp_m.group(2)), int(tmp_m.group(3)), \
                                    int(tmp_m.group(4)), int(tmp_m.group(5)), int(tmp_m.group(6)))
            return time_parsed
        
        tmp_m = self._PATTERN_TIME_1.match(text)
        if tmp_m:
            ymd_time = tmp_m.group(1)
            ymd_time = self._parse_ymd_time(ymd_time)
            hms_time = tmp_m.group(2)
            hms_time = self._parse_hms_time(hms_time)

            time_parsed = datetime(ymd_time.year, ymd_time.month, ymd_time.day, \
                                    hms_time.hour, hms_time.minute, hms_time.second)
            return time_parsed

        time_parsed = self._parse_ymd_time(text)
        if time_parsed != None:
            return time_parsed

        time_parsed = self._parse_hms_time(text)
        if time_parsed != None:
            return time_parsed

        return time_parsed

    def _parse_text_time(self, text):
        time_parsed = None

        tz = pytz.timezone(self.timezone)
        current_time = datetime.now(tz)

        if text == 'now':
            time_parsed = current_time
            return time_parsed

        if text == 'today' or text == 'tonight':
            time_parsed = datetime(current_time.year, current_time.month, current_time.day, \
                                23, 59, 59)
            return time_parsed


        # elif input_text == 'tomorrow' or input_text == 'tomorrow night':
        #   ref_time = None
        # elif input_text == 'monday':
        #   ref_time = None
        # elif input_text == 'coming monday':
        #   ref_time = None
        # elif input_text == 'last monday':
        #   ref_time = None
        # elif input_text == 'next monday':
        #   ref_time = None
        # elif input_text == 'this monday':
        #   ref_time = None

        return time_parsed

    def add_delta_time(self, **kwarg):
        datetime_obj = self.to_datetime_obj()
        datetime_obj += timedelta(**kwarg)
        return Time(datetime_obj.strftime("%Y-%m-%d %H:%M:%S"), timezone=self.timezone) 

    @staticmethod
    def parse_timezone(timezone_text):
        timezone = timezone_text.strip().lower()
        if timezone in CUSTOM_TIMEZONE:
            timezone = CUSTOM_TIMEZONE[timezone]
        else:
            timezone = 'UTC'
        return timezone

    @staticmethod
    def delta_time_str(time_1, time_2, timezone='UTC'):
        # delta time should be calculated in the same timezone
        # because the format would be different for different timezone?
        datetime_obj_1 = Time(time_1, timezone=timezone).to_datetime_obj()
        datetime_obj_2 = Time(time_2, timezone=timezone).to_datetime_obj()
        return (datetime_obj_1 - datetime_obj_2)

    @staticmethod
    def compare_time_str(time_1, time_2, timezone_1='UTC', timezone_2='UTC'):
        # convert both time to time in 'UTC' and calculate time difference
        datetime_obj_1 = Time(time_1, timezone=timezone_1).to_UTC_time().to_datetime_obj()
        datetime_obj_2 = Time(time_2, timezone=timezone_2).to_UTC_time().to_datetime_obj()
        return (datetime_obj_1 - datetime_obj_2).total_seconds()

    @staticmethod
    def parse_period(text):
        # everyday for 7 days
        # every 2 days for 30 days
        day_interval = None
        day_duration = None
        text = text.strip().lower()
        if not day_interval: 
            tmp_m = Time._PATTERN_PERIOD_0.match(text)
            if tmp_m:
                day_interval = 1
                day_duration = int(tmp_m.group(1))
        if not day_interval: 
            tmp_m = Time._PATTERN_PERIOD_1.match(text)
            if tmp_m:
                day_interval = int(tmp_m.group(1))
                day_duration = int(tmp_m.group(2))      
        return day_interval, day_duration

