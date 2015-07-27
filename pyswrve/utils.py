# -*- coding: utf-8 -*-

import requests, os.path, csv, re, sys
from tempfile import NamedTemporaryFile
from datetime import date, timedelta
from time import sleep
from socket import error as socket_error
    
if sys.version_info[0] < 3:  # Python 2
    from urlparse import urlsplit
    from ConfigParser import SafeConfigParser
    from Queue import Queue
else:  # Python 3
    from urllib.parse import urlsplit
    from configparser import SafeConfigParser
    from queue import Queue

### --- User DB Downloads --- ###
class Downloader(object):
    
    # INI config file parser
    __prs = SafeConfigParser()
    defaults = {}
    
    def __init__(self, api_key=None, personal_key=None, section=None, 
                 conf_path=None, max_attempts=10):
        
        section = section or 'defaults'
        
        # If not set on constructor load api and personal keys from config
        if not (api_key and personal_key):
            r = self.read_conf(section, conf_path)
            if not r:
                print('You need to set api key & personal key!')
        else:
            self.defaults['api_key'] = api_key
            self.defaults['personal_key'] = personal_key
        self.q = Queue()
        
        self.max_attempts = max_attempts
    
    def read_conf(self, section, conf_path):
        ''' Read $HOME/.pyswrve config file '''
        
        conf_path = conf_path or os.path.join(os.path.expanduser('~'), 
                                              '.pyswrve')
        if not os.path.exists(conf_path):
            return False
        self.__prs.read(conf_path)
        
        api_key = self.__prs.get(section, 'api_key')
        personal_key = self.__prs.get(section, 'personal_key')
        
        self.defaults['api_key'] = api_key
        self.defaults['personal_key'] = personal_key
        
        return True    
        
    def get_urls(self, item, sec='data_files'):
        ''' Get urls list from swrve '''
        
        req = requests.get('https://dashboard.swrve.com/api/1/userdbs.json', 
                           params=self.defaults).json()
        
        if type(req[sec][item]) == list:
            return req[sec][item]
        else:
            return [req[sec][item]]
            
    def download_file(self, url, path, mark_task=False, delay=None):
        ''' Download file '''
        
        # Get file name from url and join it to path
        fpath = os.path.join(path, os.path.split(urlsplit(url)[2])[1])
        
        # Request file and save it
        attempts_counter = 1
        while attempts_counter <= self.max_attempts:
            # If connection reset by pear (for exeample) 
            # restart file downloading
            try:
                req = requests.get(url, params=self.defaults, stream=True)
                with open(fpath, 'w') as f:
                    for i in req.iter_content(chunk_size=1024):
                        if i:
                            f.write(i)
                            f.flush()
                print('%s download complete' % fpath)
                break
            except socket_error:
                msg = '%s downloading error. Restarting. Attempt: %s / %s'
                print(msg % (fpath, attempts_counter, self.max_attempts))
                attempts_counter += 1
        
        # Mark this task as done and start next queue's file download
        if mark_task:
            if delay:
                sleep(delay)
            self.q.task_done()
            self.download_start(path)
        
    def load_to_queue(self, lst):
        ''' Paste urls from list to download queue '''
        
        for item in lst:
            self.q.put(item)
            
    def download_start(self, path, delay=None):
        ''' Start download of next queue's file '''
        
        if not self.q.empty():
            self.download_file(self.q.get(block=True), path, True, delay)
        else:
            print('All downloads are complete')

### --- Data selector --- ###
class DataSelector(object):
    ''' 
    Class for selection data from some period 
    by query like value > period's average, etc...
    '''
    
    head = ['DATE', 'VALUE']
    
    def __init__(self, data=None):

        self.input_data = data or []  # input data
        
        # Dicts for processed data with only days suitable for query
        self.data = {}  # with absolute values
        self.data_prc = {} # relative values (in %)
    
    def select_all_days(self, data=None):
        ''' Load all dayes without any query '''
        
        data = data or self.input_data
        if not data:
            print('You need to set data first!')
            return
        
        for i in data:
            self.data[i[0]] = [i[1]]
            self.data_prc[i[0]] = [i[1]]
    
    def select_problem_days_avr(self, compare='gt', data=None):
        ''' 
        Calculate average for period and save some days 
        after compare (default compare - greater then average)
        '''
        
        data = data or self.input_data
        if not data:
            print('You need to set data first!')
            return
        
        data_dct = {}  # dict {value: date}
        for i in data:
            data_dct[i[1]] = i[0]
        
        # Calc average
        avr = sum(data_dct.keys()) / float(len(data_dct.keys()))

        if compare == 'gt':  # >
            for key in data_dct.keys():
                if float(key) > avr:
                    self.data[data_dct[key]] = [key]  # {date: val}
                    self.data_prc[data_dct[key]] = [key]
        elif compare == 'ge':  # >=
            for key in data_dct.keys():
                if float(key) >= avr:
                    self.data[data_dct[key]] = [key]
                    self.data_prc[data_dct[key]] = [key]
        elif compare == 'lt':  # <
             for key in data_dct.keys():
                if float(key) < avr:
                    self.data[data_dct[key]] = [key]
                    self.data_prc[data_dct[key]] = [key]
        elif compare == 'le':  # <=
            for key in data_dct.keys():
                if float(key) <= avr:
                    self.data[data_dct[key]] = [key]
                    self.data_prc[data_dct[key]] = [key]
    
    def add_segment(self, seg_data, seg_name):
        ''' Load data for one segment '''
        
        # Check every day in data and select exists in self.data
        for day in seg_data:
            if day[0] in self.data.keys():  # if day in data keys
                if not seg_name in self.head:
                    self.head.append(seg_name)  # add segment to head
                
                self.data[day[0]].append(day[1])  # append value
                
                if day[1]:  # append percent %
                    v = (float(day[1]) / self.data[day[0]][0]) * 100.00
                    self.data_prc[day[0]].append(v)
                else:
                    self.data_prc[day[0]].append(0)
                    
    def make_results_list(self, prc=False, with_head=False, fix_date=False):
        ''' 
        Transform data from dict to list for easy output
        If prc - will be used relative values (in %), else absolute values
        with_head - append head list to results beggining
        fix_date - D-2015-01-31 => 2015-01-31
        Return list with lists like [[D-2015-01-31, 105, 123, 928], ...]
        '''
        
        results = []
        if with_head:  # head
            results.append(self.head)
            
        if prc:
            data = self.data_prc  # relative values
        else:
            data = self.data  # absolute values
        
        for key in data:  # append as list like [DATE, value1, value2, ...]
            if fix_date:
                d = re.sub('D-2', '2', key)  # D-2015-01-31 => 2015-01-31
            else:
                d = key
            results.append([d] + data[key])  # [D-2015-01-31, 105, 123]
            
        return results

### --- Functions --- ###
def aggregate_weeks(data, day_average=False):
    ''' Aggregate days data by weeks '''
    
    week_data = []
    
    start_week = data[0][0].split('-')
    for i in range(1, 4):
        start_week[i] = int(start_week[i])
    start_week = date(start_week[1], start_week[2], start_week[3])
    
    week_value = 0
    i = 0
    for day in data:
        if i < 6:
            week_value += day[1]
            i += 1
        else:
            week_value += day[1]
            if day_average:
                week_data.append([str(start_week), round(week_value / 7.0, 4)])
            else:
                week_data.append([str(start_week), week_value])
            start_week += timedelta(days=7)
            i = 0
            week_value = 0
    
    if len(data) % 7:
        date_week = str(start_week) + ' (%s / 7)' % i
        if day_average:
            week_data.append([date_week, round(week_value / float(i), 4)])
        else:
            week_data.append([date_week, week_value])        
    
    return week_data 

def str2date(str_date):
    ''' Convert string to datetime.date '''
    
    str_date = str_date.split('-')
    for i in range(3):
        str_date[i] = int(str_date[i])
    
    return date(str_date[0], str_date[1], str_date[2])

def list2dict(lst, head=None):
    ''' 
    Transform list with lists (as rows) to dict where 
    keys are cols headers and values are cols 
    '''

    if not head:
        head = lst[0]
        lst = lst[1:]
        
    index_dct = {}
    results_dct = {}
    for i in range(len(head)):
        index_dct[i] = head[i]
        results_dct[head[i]] = []
    
    for line in lst:
        for i in range(len(line)):
            results_dct[index_dct[i]].append(line[i])
    
    return results_dct

def save_to_csv(data, head=None, fname=None):
    ''' Write data to csv file '''
    
    if fname:  # file path selected by user
        f = open(fname, 'w')
    else:  # temp file
        f = NamedTemporaryFile(suffix='.csv', prefix='pyswrve_', delete=False)
        fname = f.name

    # Data can be dict from api.SwrveSession.get_evt_stat 
    # if method return dict with payload
    if type(data) == dict:
        
        # If data[key] = [ [DATE, value], [DATE2, value2] ... ]
        if type(data[data.keys()[0]][0]) == list:
            fields = ['DATE'] + data.keys()
            l = True
        else:  # data[key] = [value1, value2, ... ]
            fields = data.keys()
            l = False
        
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        
        for i in range(len(data[data.keys()[0]])):
            row = {}
            for key in data.keys():
                if l:  # data[key][i] == ['D-2015-01-31', 125.00]
                    row[key] = data[key][i][1]
                else:  # data[key][i] = 125.00
                    row[key] = data[key][i]
            
            if l:  # DATE 
                row['DATE'] = data[data.keys()[0]][i][0]
            
            w.writerow(row)

    # Data can be list with KPI, events fired, etc...            
    elif type(data) == list:
        w = csv.writer(f)
        
        if head:
            w.writerow(head)
        
        # data[0] == ['D-2015-01-31', 125.00]
        if type(data[0]) == list:
            w.writerows(data)
        else:  # data = [100.00, 125.00, 150.00 ... ]
            w.writerows([[i] for i in data])    
        
    f.close()
    print('File %s saved' % fname)

def generate_pyplot_styles(count=None, with_black=False, with_white=False):
    ''' 
    Generate list with line styles for drawing plots with matplotlib 
    Return list 
    '''
    
    markers = ['.', ',', 'o', 'v', '^', '<', '>']
    for i in range(1, 5):
        markers.append(str(i))
    markers += ['s', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_']

    colors = 'bgrcmy'
    if with_black:
        colors += 'k'
    if with_white:
        colors += 'w'

    styles = []
    for marker in markers:
        for linestyle in ['-', '--', '-.', ':']:
            for color in colors:
                styles.append(color+marker+linestyle)
                
    count = count or len(styles)
                
    return styles[:count]

def generate_dates_list(start, stop):
    ''' Generate list with dates as strings like '2015-01-31' '''
    
    dates_list = []
    
    # '2015-05-14' => (2015, 5, 14)
    start = start.split('-')
    stop = stop.split('-')
    for i in range(3):
        start[i] = int(start[i])
        stop[i] = int(stop[i])
    
    # dt since start to stop
    dt = date(stop[0], stop[1], stop[2]) - date(start[0], start[1], start[2])
    
    for i in range(dt.days+1):
        d = str(date(start[0], start[1], start[2]) + timedelta(days=i))
        dates_list.append(d)
        
    return dates_list

def postgresql_custom_properties_fix(fname):
    ''' Fix custom_properties csv file for loading to PostgreSQL '''
    
    with open(fname) as f:
        data = f.read()
    
    data = re.sub('\\\,', '.', data)  # iPhone7,2 => iPhone7.2
    data = re.sub(',\r,', ',,', data)  # fix rows splitted in the middle
    data = re.sub(',\",', ',0,', data)  # fix " on level's pos
    
    with open(fname, 'w') as f:
        f.write(data)
