# -*- coding: utf-8 -*-

import os
import json
from unittest import mock
from datetime import datetime, timedelta

import vcr

from pyswrve import ExportApi


class TestExportApi:
    """ Class for testing ExportApi methods.
    Before testing:
        1. Save `api_key` and `personal_key` to `$HOME/.pyswrve`
        2. Create and modify `tests/names.json`
    """

    period_len = 7
    start = datetime(2017, 1, 1)
    stop = start + timedelta(days=period_len-1)

    cassette_path = 'tests/vcr_cassettes/%s.yml'
    skip_lst = ['api_key', 'personal_key']

    names_path = 'tests/names.json'
    with open(names_path) as jf:
        names_dct = json.load(jf)

    @vcr.use_cassette(cassette_path % 'kpi', filter_query_parameters=skip_lst)
    def test_get_kpi(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)

        res = api.get_kpi('dau')
        assert isinstance(res, list)
        assert isinstance(res[0][0], str)
        assert len(res) == self.period_len

    @vcr.use_cassette(cassette_path % 'kpi-without-date',
                      filter_query_parameters=skip_lst)
    def test_get_kpi_without_date(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)

        res = api.get_kpi('dau', with_date=False)
        assert isinstance(res, list)
        assert len(res) == self.period_len

    @vcr.use_cassette(cassette_path % 'kpi-datetime',
                      filter_query_parameters=skip_lst)
    def test_get_kpi_datetime(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)

        res = api.get_kpi('dau', as_datetime=True)
        assert isinstance(res[0][0], datetime)

    @mock.patch.dict(os.environ, names_dct['evt'])
    @vcr.use_cassette(cassette_path % 'evt', filter_query_parameters=skip_lst)
    def test_get_evt(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)
        evt_name = os.environ['evt_name']

        res = api.get_evt(evt_name)
        assert isinstance(res, list)
        assert isinstance(res[0][0], str)
        assert len(res) == self.period_len

    @mock.patch.dict(os.environ, names_dct['evt'])
    @vcr.use_cassette(cassette_path % 'evt-without-date',
                      filter_query_parameters=skip_lst)
    def test_get_evt_without_date(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)
        evt_name = os.environ['evt_name']

        res = api.get_evt(evt_name, with_date=False)
        assert isinstance(res, list)
        assert len(res) == self.period_len

    @mock.patch.dict(os.environ, names_dct['evt'])
    @vcr.use_cassette(cassette_path % 'evt-datetime',
                      filter_query_parameters=skip_lst)
    def test_get_evt_datetime(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)
        evt_name = os.environ['evt_name']

        res = api.get_evt(evt_name, as_datetime=True)
        assert isinstance(res[0][0], datetime)

    @vcr.use_cassette(cassette_path % 'evt-lst',
                      filter_query_parameters=skip_lst)
    def test_get_evt_lst(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)
        res = api.get_evt_lst()

        assert isinstance(res, list)

    @mock.patch.dict(os.environ, names_dct['evt'])
    @vcr.use_cassette(cassette_path % 'payload',
                      filter_query_parameters=skip_lst)
    def test_get_payload(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)
        evt_name = os.environ['evt_name']
        payload_key = os.environ['payload_key']
        res = api.get_payload(evt_name, payload_key, default_struct=False)

        assert isinstance(res, list)
        assert len(res) == self.period_len

    @mock.patch.dict(os.environ, names_dct['evt'])
    @vcr.use_cassette(cassette_path % 'payload-lst',
                      filter_query_parameters=skip_lst)
    def test_get_payload_lst(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)
        evt_name = os.environ['evt_name']
        res = api.get_payload_lst(evt_name)

        assert isinstance(res, list)

    @vcr.use_cassette(cassette_path % 'user-cohorts',
                      filter_query_parameters=skip_lst)
    def test_get_user_cohorts(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)
        res = api.get_user_cohorts()

        assert isinstance(res, dict)
        assert len(res) == self.period_len

    @mock.patch.dict(os.environ, names_dct['item'])
    @vcr.use_cassette(cassette_path % 'item-sales',
                      filter_query_parameters=skip_lst)
    def test_get_item_sales(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)
        uid = os.environ['uid']
        res = api.get_item_sales(uid)

        assert isinstance(res, list)

    @mock.patch.dict(os.environ, names_dct['item'])
    @vcr.use_cassette(cassette_path % 'item-revenue',
                      filter_query_parameters=skip_lst)
    def test_get_item_revenue(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)
        uid = os.environ['uid']
        res = api.get_item_revenue(uid)

        assert isinstance(res, list)

    @mock.patch.dict(os.environ, names_dct['tag'])
    @vcr.use_cassette(cassette_path % 'item-tag',
                      filter_query_parameters=skip_lst)
    def test_get_item_tag(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)
        tag = os.environ['tag']
        res = api.get_item_tag(tag)

        assert isinstance(res, list)

    @vcr.use_cassette(cassette_path % 'segment-lst',
                      filter_query_parameters=skip_lst)
    def test_get_segment_lst(self):
        api = ExportApi()
        api.set_dates(self.start, self.stop)
        res = api.get_segment_lst()

        assert isinstance(res, list)
