# -*- coding: utf-8 -*-

import os.path
from configparser import SafeConfigParser

import requests

from .exceptions import SwrveApiException


class SwrveApi:
    """ Base class for senfing requests to Swrve Non-Client APIs

    https://docs.swrve.com/swrves-apis/non-client-apis
    """

    conf_path = os.path.join(os.path.expanduser('~'), '.pyswrve')
    __conf = SafeConfigParser()

    __api_url_us = 'https://dashboard.swrve.com/api/1/'
    __api_url_eu = 'https://eu-dashboard.swrve.com/api/1/'
    _api_url = None

    def __init__(self, region='us', api_key=None, personal_key=None,
                 section=None, conf_path=None):
        """ __init__

        :param region: [:class:`str`] us or eu region, it defines domain
            in urls - dashboard.swrve.com or eu-dashboard.swrve.com
        :param api_key: [:class:`str`] API Key from Swrve Dashboard -
            Setup -  Integration Settings - App Information
        :param personal_key: [:class:`str`] Your personal key from
            Swrve Dashboard Setup -  Integration Settings
        :param section: [:class:`str`] section in pyswrve config, you
            are able to store keys for different projects in different
            config sections
        :param conf_path: [:class:`str`] arg overrides default path to
            config file with entered
        """

        if section is None:
            section = 'defaults'
        self.section = section

        if not api_key or not personal_key:
            if conf_path is not None:
                self.con_path = conf_path

            self.__conf.read(self.conf_path)
            api_key = self.__conf.get(section, 'api_key')
            personal_key = self.__conf.get(section, 'personal_key')

        self._params = {
            'api_key': api_key,
            'personal_key': personal_key
        }

        if region == 'us':
            self._api_url = self.__api_url_us
        elif region == 'eu':
            self._api_url = self.__api_url_eu

    def save_config(self):
        """ Save params to config file """

        for key in self._params:
            val = self._params[key]
            self.__conf.set(self.section, key, val)

        with open(self.conf_path, 'w') as f:
            self.__conf.write(f)

    def set_param(self, key, val):
        self._params[key] = val

    def send_api_request(self, url, **kwargs):
        """ Send GET request to Swrve API

        :param url: [:class:`str`] url for request
        :return: [:class:`dict`] request results
        :raises SwrveApiException: if request status_code != 200
        """

        params = self._params.copy()
        dct = {k: kwargs[k] for k in kwargs if kwargs[k] is not None}
        params.update(dct)

        res = requests.get(url, params=params)
        if res.status_code != 200:
            try:
                error = res.json()['error']
            except ValueError:
                error = None
            raise SwrveApiException(error, res.status_code, url, params)

        return res.json()
