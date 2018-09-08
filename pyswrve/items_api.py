# -*- coding: utf-8 -*-

import json
from urllib.parse import urljoin

import requests

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

    def send_post_request(self, url, uid=None, data=None):
        """ Send POST request to Swrve Items API

        :param url: [:class:`str`] url for request
        :raises SwrveApiException: if request status_code != 200
        """

        params = self._params.copy()
        if uid is not None:
            params['item'] = uid
        if data is not None:
            params['data'] = json.dumps(data)

        requests.post(url, data=params)

    def get_item_lst(self):
        """ Request list of project items

        :return: [:class:`list`] a list with dicts with info about items
        """

        results = self.send_api_request(self._api_url)
        return results

    def get_item_attrs(self, uid):
        """ Request list of item attributes

        :return: [:class:`dict`] a dict with item attributes
        """

        results = self.send_api_request(self._api_url, item=uid)
        return results

    def create_item(self, uid, data=None):
        """ Create or update one item

        :param uid: [:class:`str`] an unique id of the item
        :param data: [:class:`dict`] a dict of standart parameters and
            custom attributes of the item, next keys are used as
            parameters: `name`, `item_class`, `thumbnail`, `description`,
            and any other keys are used as attributes
        """

        url = self._api_url
        self.send_post_request(url, uid, data)

    def create_items(self, data=None):
        """ Create a batch of items

        :param data: [:class:`dict`] a dict of dicts, where keys are
            unique items ids and values are dicts of standart parameters
            and custom attributes of the items (next keys are used as
            parameters: `name`, `item_class`, `thumbnail`, `description`,
            and any other keys are used as attributes)
        """

        url = self._api_url + '_bulk'
        self.send_post_request(url, data=data)
