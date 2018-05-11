# -*- coding: utf-8 -*-

import os.path
from time import sleep
from queue import Queue
from urllib.parse import urlsplit
from socket import error as socket_error
from configparser import SafeConfigParser

import requests


class Downloader:

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
        """ Read $HOME/.pyswrve config file """

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
        """ Get urls list from swrve """

        req = requests.get('https://dashboard.swrve.com/api/1/userdbs.json',
                           params=self.defaults).json()

        if item == 'all':
            return req[sec]

        if isinstance(req[sec][item], list):
            return req[sec][item]
        else:
            return [req[sec][item]]

    def download_file(self, url, path, mark_task=False, delay=None):

        # Get file name from url and join it to path
        fpath = os.path.join(path, os.path.split(urlsplit(url)[2])[1])

        # Request file and save it
        attempts_counter = 1
        while attempts_counter <= self.max_attempts:
            # Restart downloadinf on fail
            try:
                req = requests.get(url, params=self.defaults, stream=True)
                with open(fpath, 'wb') as f:
                    for i in req.iter_content(chunk_size=1024):
                        if i:
                            f.write(i)
                            f.flush()
                break
            except socket_error:
                attempts_counter += 1

        # Mark this task as done and start next queue's file download
        if mark_task:
            if delay:
                sleep(delay)
            self.q.task_done()
            self.download_start(path)

    def load_to_queue(self, lst):
        """" Paste urls from list to download queue """

        for item in lst:
            self.q.put(item)

    def download_start(self, path, delay=None):
        """ Start download of next queue's file """

        if not self.q.empty():
            self.download_file(self.q.get(block=True), path, True, delay)
