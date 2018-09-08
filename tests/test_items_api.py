# -*- coding: utf-8 -*-

import os
import json
from unittest import mock

import vcr

from pyswrve import ItemsApi


class TestItemsApi:
    """ Class for testing ItemsApi methods.
    Before testing:
        1. Save `api_key` and `personal_key` to `$HOME/.pyswrve`
        2. Create and modify `tests/names.json`
    """

    cassette_path = 'tests/vcr_cassettes/%s.yml'
    skip_lst = ['api_key', 'personal_key']

    names_path = 'tests/names.json'
    with open(names_path) as jf:
        names_dct = json.load(jf)

    @vcr.use_cassette(cassette_path % 'item-lst',
                      filter_query_parameters=skip_lst)
    def test_get_item_lst(self):
        api = ItemsApi()
        res = api.get_item_lst()
        assert isinstance(res, list)
        assert isinstance(res[0], dict)

    @mock.patch.dict(os.environ, names_dct['item'])
    @vcr.use_cassette(cassette_path % 'item-attrs',
                      filter_query_parameters=skip_lst)
    def test_get_item_attrs(self):
        api = ItemsApi()
        uid = os.environ['uid']
        res = api.get_item_attrs(uid)
        assert isinstance(res, dict)
