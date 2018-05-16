# -*- coding: utf-8 -*-

from urllib.parse import urljoin

from .api import SwrveApi


class SwrveUserdbApi(SwrveApi):
    """
    Class for requesting and downloading UserDB with Swrve Export API

    https://docs.swrve.com/swrves-apis/non-client-apis/\
swrve-export-api-guide/#User_DB_Export
    """

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

        super().__init__(region, api_key, personal_key, section, conf_path)
        self._api_url = urljoin(self._api_url, 'userdbs.json')

    def get_urls(self):
        """ Request urls list for UserDB download

        :return: [:class:`dict`] dict with urls for data files, schemas
        """

        return self.send_api_request(self._api_url)
