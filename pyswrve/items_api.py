# -*- coding: utf-8 -*-

from urllib.parse import urljoin

from .api import SwrveApi


class SwrveItemsApi(SwrveApi):
    """
    Class for viewing/creating/updating items with Swrve Items API

    https://docs.swrve.com/swrves-apis/non-client-apis/swrve-items-api-guide
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
        self._api_url = urljoin(self._api_url, 'items')

    def get_item_lst(self):
        """ Request list of project items

        :return: [:class:`list`] a list with items
        """

        results = self.send_api_request(self._api_url)
        return results

    def get_item_attrs(self, item_id):
        """ Request list of item attributes

        :return: [:class:`list`] a list with attributes
        """

        results = self.send_api_request(self._api_url, item=item_id)
        return results
