# -*- coding: utf-8 -*-

import vcr

from pyswrve import UserdbApi


class TestUserdbApi:
    """ Class for testing UserdbApi methods.
    Before testing:
        1. Save `api_key` and `personal_key` to `$HOME/.pyswrve`
    """

    cassette_path = 'tests/vcr_cassettes/%s.yml'
    skip_lst = ['api_key', 'personal_key']

    @vcr.use_cassette(cassette_path % 'urls', filter_query_parameters=skip_lst)
    def test_get_urls(self):
        api = UserdbApi()
        res = api.get_urls()

        assert isinstance(res, dict)

        keys = {'data_files', 'schemas', 'date'}
        assert set(keys).issubset(res.keys())
