# -*- coding: utf-8 -*-

from urllib.parse import urljoin
from datetime import datetime, timedelta

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

        if isinstance(start, datetime):
            start = start.strftime('%Y-%m-%d')
        if isinstance(stop, datetime):
            stop = stop.strftime('%Y-%m-%d')

        self.set_param('start', start)
        self.set_param('stop', stop)

    def get_kpi(self, kpi, with_date=True, currency=None, segment=None,
                multiplier=None):
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
        :param segment: [:class:`str`] request stats for specified segment
        :param multiplier: [:class:`float`] revenue multiplier like in Swrve
            Dashboard - Setup - Report Settings - Reporting Revenue,
            it applies to revenue, arpu and arppu
        :return: [:class:`list`] a list of lists with dates and values or
            a list of values, it depends on with_date arg
        """

        url = urljoin(self._api_url, 'kpi/%s.json' % kpi)
        data = self.send_api_request(url, currency=currency, segment=segment)
        results = data[0]['data']

        if multiplier is not None and kpi in self.kpi_taxable:
            results = [[i[0], i[1]*multiplier] for i in data]

        if not with_date:
            results = [i[1] for i in data]

        return results

    def get_kpi_dau(self, kpi, with_date=True, currency=None, segment=None,
                    multiplier=None):
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
        :param segment: [:class:`str`] request stats for specified segment
        :param multiplier: [:class:`float`] revenue multiplier like in Swrve
            Dashboard - Setup - Report Settings - Reporting Revenue,
            it applies to revenue, arpu and arppu
        :return: [:class:`list`] a list of lists with dates and values or
            a list of values, it depends on with_date arg
        """

        data = {}
        for k in ('dau', kpi):
            data[k] = self.get_kpi(k, with_date, currency, segment, multiplier)

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

    def get_evt(self, evt_name, with_date=True, segment=None):
        """ Request event stats

        :param evt_name: [:class:`str`] the event name
        :param with_date: [`bool`] by default swrve return every element
            as [['D-2015-01-31', 126.0], ['D-2015-01-31', 116.0]] so
            the result is a list of lists, if `with_date` setted to `True`
            the original result is modifing to list of values like
            [126.0, 116.0]
        :param segment: [:class:`str`] request stats for specified segment
        :return: [:class:`list`] a list of lists with dates and values or
            a list of values, it depends on with_date arg
        """

        url = urljoin(self._api_url, 'event/count')
        data = self.send_api_request(url, name=evt_name, segment=segment)
        results = data[0]['data']
        if not with_date:
            results = [i[1] for i in data]

        return results

    def get_evt_dau(self, evt_name, with_date=True, segment=None):
        """ Request event stats and divide every value with DAU

        :param evt_name: [:class:`str`] the event name
        :param with_date: [`bool`] by default swrve return every element
            as [['D-2015-01-31', 126.0], ['D-2015-01-31', 116.0]] so
            the result is a list of lists, if `with_date` setted to `True`
            the original result is modifing to list of values like
            [126.0, 116.0]
        :param segment: [:class:`str`] request stats for specified segment
        :return: [:class:`list`] a list of lists with dates and values or
            a list of values, it depends on with_date arg
        """

        data = {
            'dau': self.get_kpi('dau', with_date, segment=segment),
            evt_name: self.get_evt(evt_name, with_date, segment)
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
        results = self.send_api_request(url)

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
        data = self.send_api_request(url, name=evt_name,
                                     payload_key=payload_key)

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
        results = self.send_api_request(url, name=evt_name)

        return results

    def get_user_cohorts(self, cohort_type='retention', segment=None):
        """ Request user cohorts data

        :param cohort_type: [:class:`str`] the type of cohort data to be
            requested: retention, avg_sessions, avg_playtime, avg_revenue or
            total_revenue
        :param segment: [:class:`str`] request stats for specified segment
        :return: [:class:`dict`] a dict where keys are where cohorts dates
            and values are dicts with cohort info
        """

        url = urljoin(self._api_url, 'cohorts/daily')
        results = self.send_api_request(url, cohort_type=cohort_type,
                                        segment=segment)

        return results[0]['data']

    def get_item_sales(self, uid=None, tag=None, currency=None,  segment=None):
        """ Request the sales (count) of the item(s). If no uid or tag is
        specified, requests all items.

        :param uid: [:class:`str`] uid of the item
        :param tag: [:class:`str`] tag of the items
        :param currency: [:class:`str`] if currency is None requests for all
        :param segment: request stats for specified segment
        :return: [:class:`list`] a list of dicts, one dict - one currency
        """

        url = urljoin(self._api_url, 'item/sales')
        results = self.send_api_request(url, uid=uid, tag=tag,
                                        currency=currency, segment=segment)
        return results

    def get_item_revenue(self, uid=None, tag=None, currency=None,
                         segment=None):
        """ Request revenue (count * price) from the item(s). If no uid or
        tag is specified, requests all items.

        :param uid: [:class:`str`] uid of the item
        :param tag: [:class:`str`] tag of the items
        :param currency: [:class:`str`] if currency is None requests for all
        :param segment: request stats for specified segment
        :return: [:class:`list`] a list of dicts, one dict - one currency
        """

        url = urljoin(self._api_url, 'item/revenue')
        results = self.send_api_request(url, uid=uid, tag=tag,
                                        currency=currency, segment=segment)
        return results

    def get_item_tag(self, tag):
        """ Request uids of all items that are associated with the tag

        :param tag: [:class:`str`] resources tag
        :return: [:class:`list`] list of dicts with uids and names
        """

        url = urljoin(self._api_url, 'item/tag')
        results = self.send_api_request(url, tag=tag)
        return results

    def get_segment_lst(self):
        """ Request prject segments list

        :return: [:class:`list`] a list with segments
        """

        url = urljoin(self._api_url, 'segment/list')
        results = self.send_api_request(url)

        return results
