# -*- coding: utf-8 -*-

from urllib.parse import urljoin
from datetime import datetime, timedelta

import requests

from .api import SwrveApi


class SwrveExportApi(SwrveApi):
    """ Class for requesting stats with Swrve Export API

    https://docs.swrve.com/swrves-apis/non-client-apis/swrve-export-api-guide
    """

    kpi_factors = {'dau', 'mau', 'dau_mau', 'new_users', 'dpu', 'conversion',
                   'dollar_revenue', 'currency_spent', 'currency_spent_dau',
                   'currency_purchased', 'currency_purchased_dau',
                   'currency_given', 'items_purchased', 'items_purchased_dau',
                   'session_count', 'avg_session_length', 'arpu_daily',
                   'arppu_daily', 'arpu_monthly', 'arppu_monthly',
                   'avg_playtime', 'day30_retention'}

    for i in (1, 3, 7):
        kpi_factors.add('day%s_reengagement' % i)
        kpi_factors.add('day%s_retention' % i)

    kpi_taxable = {'dollar_revenue', 'arpu_daily', 'arppu_daily',
                   'arpu_monthly', 'arppu_monthly'}
    period_lens = {'day': 1, 'week': 7, 'month': 30, 'year': 360}

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
        self._api_url = urljoin(self._api_url, 'exporter/')

    def set_dates(self, start=None, stop=None, period=None, period_len=None):
        """ Set start and stop or history params

        :param start: period's first date
        :type start: datetime, str
        :param stop: period's last date
        :type stop: datetime, str
        :param period: [:class:`str`] day, week, month or year
        :period_len: [:class:`int`] count of days (weeks, etc) in period
        """

        if period:
            if period_len is None:
                period_len = 1
            stop = datetime.today()
            days = period_len * self.period_lens(period)
            start = stop - timedelta(days=days)

        for _date in (start, stop):
            if isinstance(_date, datetime):
                _date = _date.strftime('%Y-%m-%d')

        self.set_param('start', start)
        self.set_param('stop', stop)

    def get_kpi(self, kpi, with_date=True, currency=None, multiplier=None):
        """ Request the kpi stats

        :param kpi: [:class:`str`] the kpi's name, one from
            `SwrveExportApi.kpi_factors`
        :param with_date: [`bool`] by default swrve return every element
            as [['D-2015-01-31', 126.0], ['D-2015-01-31', 116.0]] so
            the result is a list of lists, if `with_date` setted to `True`
            the original result is modifing to list of values like
            [126.0, 116.0]
        :param currency: [:class:`str`] in-project currency, used for kpis
            like currency_given
        :param multiplier: [:class:`float`] revenue multiplier like in Swrve
            Dashboard - Setup - Report Settings - Reporting Revenue,
            it applies to revenue, arpu and arppu
        :return: [:class:`list`] a list of lists with dates and values or
            a list of values, it depends on with_date arg
        """

        url = urljoin(self._api_url, 'kpi/%s.json' % kpi)
        params = self._params.copy()
        if currency:
            params['currency'] = currency

        data = self.send_api_request(url, params)
        results = data[0]['data']

        if multiplier is not None and kpi in self.kpi_taxable:
            results = [[i[0], i[1]*multiplier] for i in data]

        if not with_date:
            results = [i[1] for i in data]

        return results

    def get_kpi_dau(self, kpi, with_date=True, currency=None, multiplier=None):
        """" Request the kpi stats and divide every value with DAU

        :param kpi: [:class:`str`] the kpi's name, one from
            `SwrveExportApi.kpi_factors`
        :param with_date: [`bool`] by default swrve return every element
            as [['D-2015-01-31', 126.0], ['D-2015-01-31', 116.0]] so
            the result is a list of lists, if `with_date` setted to `True`
            the original result is modifing to list of values like
            [126.0, 116.0]
        :param currency: [:class:`str`] in-project currency, used for kpis
            like currency_given
        :param multiplier: [:class:`float`] revenue multiplier like in Swrve
            Dashboard - Setup - Report Settings - Reporting Revenue,
            it applies to revenue, arpu and arppu
        :return: [:class:`list`] a list of lists with dates and values or
            a list of values, it depends on with_date arg
        """

        data = {}
        for k in ('dau', kpi):
            data[k] = self.get_kpi(k, with_date, currency, multiplier)

        results = []
        for idx in range(len(data['dau'])):
            _dau = data['dau'][idx]
            _kpi = data[kpi][idx]

            if _dau == 0:
                res = 0
            elif isinstance(_dau, list) and _dau[1] == 0:
                res = [0]
            elif isinstance(_dau, list):
                res = [_dau[0], _kpi[1] / _dau[1]]
            else:
                res = _kpi / _dau

            results.append([res])

        return results

    def get_evt(self, evt_name, with_date=True):
        """ Request event stats

        :param evt_name: [:class:`str`] the event name
        :param with_date: [`bool`] by default swrve return every element
            as [['D-2015-01-31', 126.0], ['D-2015-01-31', 116.0]] so
            the result is a list of lists, if `with_date` setted to `True`
            the original result is modifing to list of values like
            [126.0, 116.0]
        :return: [:class:`list`] a list of lists with dates and values or
            a list of values, it depends on with_date arg
        """

        url = urljoin(self._api_url, 'event/count')
        params = self._params.copy()
        params['name'] = evt_name
        data = self.send_api_request(url, params)
        results = data[0]['data']
        if not with_date:
            results = [i[1] for i in data]

        return results

    def get_evt_dau(self, evt_name, with_date=True):
        """ Request event stats and divide every value with DAU

        :param evt_name: [:class:`str`] the event name
        :param with_date: [`bool`] by default swrve return every element
            as [['D-2015-01-31', 126.0], ['D-2015-01-31', 116.0]] so
            the result is a list of lists, if `with_date` setted to `True`
            the original result is modifing to list of values like
            [126.0, 116.0]
        :return: [:class:`list`] a list of lists with dates and values or
            a list of values, it depends on with_date arg
        """

        data = {
            'dau': self.get_kpi('dau', with_date),
            evt_name: self.get_evt(evt_name, with_date)
        }

        results = []
        for idx in range(len(data['dau'])):
            _dau = data['dau'][idx]
            _evt = data[evt_name][idx]

            if _dau == 0:
                res = 0
            elif isinstance(_dau, list) and _dau[1] == 0:
                res = [0]
            elif isinstance(_dau, list):
                res = [_dau[0], _evt[1] / _dau[1]]
            else:
                res = _evt / _dau

            results.append([res])

        return results

    def get_evt_lst(self):
        """ Request project events list

        :return: [:class:`list`] a list with events
        """

        url = urljoin(self._api_url, 'event/list')
        params = self._params.copy()
        results = self.send_api_request(url, params)

        return results

    def get_payload(self, evt_name, payload_key, with_date=True,
                    default_struct=False):
        """ Request stats for the event with specified payload key

        :param evt_name: [:class:`str`] the event name
        :param payload_key: [:class:`str`] the payload key
        :param with_date: [`bool`] by default swrve return every element
            as [['D-2015-01-31', 126.0], ['D-2015-01-31', 116.0]] so
            the result is a list of lists, if `with_date` setted to `True`
            the original result is modifing to list of values like
            [126.0, 116.0]
        :param default_struct: [`bool`] default response data structure are

            `[{'data': [['D-2017-01-01', 160], ['D-2018-01-02', 116]],
            'event_name': 'levelup',
            'name': 'levelup/level/1',
            'payload_key': 'level',
            'payload_value': '1},
            {'data': [['D-2017-01-01', 260], ['D-2018-01-02', 216]],
            'event_name': 'levelup',
            'name': 'levelup/level/2',
            'payload_key': 'level',
            'payload_value': '2'}]`

            by setting default_struct = True the structure are transforming in

            `[{'timeline': 'D-2018-01-01', '1': 116, '2': 260},
            {'timeline': 'D-2018-01-02', '1': 116, '2': 216}]`
        :return: [:class:`list`] a list of dicts with stats for
            payload key in event
        """

        url = urljoin(self._api_url, 'event/payload')
        params = self._params.copy()
        params['name'] = evt_name
        params['payload_key'] = payload_key
        data = self.send_api_request(url, params)

        if not with_date:
            for dct in data:
                dct['data'] = [i[1] for i in dct['data']]

        if default_struct:
            return data

        results = {}
        for dct in data:
            paylod_value = dct['payload_value']

            for idx in range(len(dct['data'])):
                if isinstance(dct['data'][idx], list):
                    results_key, value = dct['data'][idx]
                else:
                    results_key = idx
                    value = dct['data'][idx]

                if results_key not in results:
                    results[results_key] = {'timeline': results_key}
                results[results_key][paylod_value] = value

        results = sorted(results.values(), key=lambda x: x['timeline'])

        return results

    def get_payload_lst(self, evt_name):
        """ Request event payloads list

        :param evt_name: [:class:`str`] the event name
        :return: [:class:`list`] a list with payloads
        """

        url = urljoin(self._api_url, 'event/payloads')
        params = self._params.copy()
        params['name'] = evt_name
        results = self.send_api_request(url, params)

        return results

    def get_user_cohorts(self, cohort_type='retention'):
        """ Request user cohorts data

        :param cohort_type: [:class:`str`] the type of cohort data to be
            requested: retention, avg_sessions, avg_playtime, avg_revenue or
            total_revenue
        :return: [:class:`dict`] a dict where keys are where cohorts dates
            and values are dicts with cohort info
        """

        url = urljoin(self._api_url, 'cohorts/daily')
        params = self._params.copy()
        params['cohort_type'] = cohort_type
        results = self.send_api_request(url, params)

        return results[0]['data']

    def get_item_sales(self, item=None, tag=None, currency=None, revenue=True,
                       with_date=True, per_user=False, params=None):
        """
        Request count of item sales or revenue from items sales

        :rtype: :class:`dict`
        """

        params = params or dict(self.defaults)  # request params
        if item:
            params['uid'] = item
        if tag:
            params['tag'] = tag
        if currency:
            params['currency'] = currency

        if revenue:
            url = 'https://dashboard.swrve.com/api/1/exporter/item/revenue'
        else:
            url = 'https://dashboard.swrve.com/api/1/exporter/item/sales'

        req = requests.get(url, params=params).json()  # do request
        # Request errors
        if isinstance(req, dict):
            if 'error' in req.keys():
                print('Error: %s' % req['error'])
                return

        data = {}
        for d in req:
            # Key for data dict 'item name - currency'
            k = '%s - %s' % (d['name'], d['currency'])
            if not with_date:
                data[k] = [i[1] for i in d['data']]
            else:
                data[k] = d['data']

        if per_user:  # calc for one user
            dau = self.get_kpi('dau', False, params=params)

            for key in data.keys():
                for i in range(len(dau)):
                    if not with_date:
                        # Check does dau[i] > 0 for ZeroDivisionError fix
                        if dau[i]:
                            data[key][i] = round(data[key][i] / dau[i], 4)
                        else:
                            data[key][i] = 0
                    else:
                        if dau[i]:
                            data[key][i][1] = round(
                                data[key][i][1] / dau[i], 4
                            )
                        else:
                            data[key][i][1] = 0

        return data

    def get_segment_lst(self, params=None):
        """ Request prject segments list

        :return: [:class:`list`] a list with segments
        """

        url = urljoin(self._api_url, 'segment/list')
        params = self._params.copy()
        results = self.send_api_request(url, params)

        return results
