# -*- coding: utf-8 -*-

import os.path
from datetime import date, timedelta
from configparser import SafeConfigParser

import requests


class SwrveSession:

    # Default swrve's KPI factors
    kpi_factors = ['dau', 'mau', 'dau_mau', 'new_users', 'dpu', 'conversion',
                   'dollar_revenue', 'currency_spent', 'currency_spent_dau',
                   'currency_purchased', 'currency_purchased_dau',
                   'currency_given', 'items_purchased', 'items_purchased_dau',
                   'session_count', 'avg_session_length', 'arpu_daily',
                   'arppu_daily', 'arpu_monthly', 'arppu_monthly',
                   'avg_playtime', 'day30_retention']

    # Factors which are need tax calculation
    kpi_taxable = ('dollar_revenue', 'arpu_daily', 'arppu_daily',
                   'arpu_monthly', 'arppu_monthly')

    for i in (1, 3, 7):
        kpi_factors.append('day%s_reengagement' % i)
        kpi_factors.append('day%s_retention' % i)

    kpi_factors = tuple(kpi_factors)  # convert list to tuple

    # INI config file parser
    __prs = SafeConfigParser()

    def __init__(self, api_key=None, personal_key=None, history=None,
                 start=None, stop=None, segment=None, section=None,
                 conf_path=None):

        self.section = section or 'defaults'

        # If not set on constructor load api and personal keys from config
        if not (api_key and personal_key):
            conf_path = conf_path or os.path.join(os.path.expanduser('~'),
                                                  '.pyswrve')
            self.__prs.read(conf_path)

            # Check does selected config section exist
            if not (self.__prs.has_section(self.section) and
                    self.__prs.has_section('defaults')):
                print('\
Selected section not found, please set api key and personal key manually')
                return
            elif not self.__prs.has_section(self.section):
                print('Selected section not found, using defaults')
                self.section = 'defaults'

            api_key = self.__prs.get(self.section, 'api_key')
            personal_key = self.__prs.get(self.section, 'personal_key')
        else:
            self.__prs.add_section(self.section)
            self.__prs.set(self.section, 'api_key', api_key)
            self.__prs.set(self.section, 'personal_key', personal_key)

        # Required by any request
        self.defaults = {
            'api_key': api_key,
            'personal_key': personal_key,
            'history': history,
            'start': start,
            'stop': stop,
            'segment': segment
        }

    def save_defaults(self):
        """" Save default params to config file """

        conf_path = os.path.join(os.path.expanduser('~'), '.pyswrve')
        with open(conf_path, 'w') as f:
            self.__prs.write(f)

    def set_param(self, param, val):
        """ Change value of param defined on object creation or \
        set one new
        """

        # FIXME: bug, need to replace param with val
        if param == 'api_key':
            self.__prs.set(self.section, 'api_key', param)
        elif param == 'personal_key':
            self.__prs.set(self.section, 'personal_key', param)

        self.defaults[param] = val

    def set_dates(self, start=None, stop=None, period=None, period_count=None):
        """ Set start and stop or history params """

        if not (start and stop or period):
            print('You need to set start & stop dates or set period')
            return
        elif period:

            # About period & period_count
            # Period = week, period_count = 3 => 3 weeks
            # Period = month, period_count = 5 => 5 months, etc...
            if not period_count:
                period_count = 1
            stop = date.today() - timedelta(days=1)

            if period == 'day':
                count = 1
            elif period == 'week':
                count = 7
            elif period == 'month':
                count = 30
            elif period == 'year':
                count = 365

            start = stop - timedelta(days=count*period_count)

        self.defaults['start'] = str(start)
        self.defaults['stop'] = str(stop)

    def get_kpi(self, factor, with_date=True, currency=None, params=None,
                tax=None):
        """ Request KPI factor data from swrve

        :rtype: :class:`list`
        """

        # Request url
        url = 'https://dashboard.swrve.com/api/1/exporter/kpi/%s.json' % factor
        params = params or dict(self.defaults)  # request params
        if currency:
            params['currency'] = currency  # cash, coins, etc...

        req = requests.get(url, params=params).json()

        # Request errors
        if isinstance(req, dict):
            if 'error' in req.keys():
                print('Error: %s' % req['error'])
                return

        if not with_date:  # without date
            if tax and (factor in self.kpi_taxable):  # with tax
                # value * (1 - tax), then round it to 2 symbols after dot
                data = [round(i[1] * (1 - tax), 2) for i in req[0]['data']]
            else:  # results without tax
                data = [i[1] for i in req[0]['data']]
        else:  # with date
            data = req[0]['data']
            if tax and (factor in self.kpi_taxable):
                for i in range(len(data)):
                    if data[i][1]:
                        data[i][1] = round(data[i][1] * (1 - tax), 2)

        return data

    def get_kpi_dau(self, factor, with_date=True, currency=None, params=None,
                    tax=None):
        """" Request data for KPI factor / DAU (per one user)

        :rtype: :class:`list`
        """

        # Request url
        url = 'https://dashboard.swrve.com/api/1/exporter/kpi/%s.json' % factor
        params = params or dict(self.defaults)  # request params
        if currency:
            params['currency'] = currency  # cash, coins, etc...

        dau = self.get_kpi('dau', False, currency, params)
        if not dau:  # dau will be None if request was failed with error
            return   # because error already was printed just return
        req = requests.get(url, params=params).json()

        fdata = req[0]['data']  # factor data
        data = []
        if not with_date:  # without date
            for i in range(len(dau)):
                # Check does dau[i] > 0 for ZeroDivisionError fix
                if dau[i]:
                    # Substract tax from value
                    if tax and (factor in self.kpi_taxable):
                        val = round((fdata[i][1] / dau[i]) * (1 - tax), 4)
                    else:  # no substraction
                        val = round(fdata[i][1] / dau[i], 4)
                else:
                    val = 0
                data.append(val)
        else:  # with date
            for i in range(len(dau)):
                if dau[i]:
                    if tax and (factor in self.kpi_taxable):
                        if fdata[i][1]:
                            fdata[i][1] = round((fdata[i][1] / dau[i])*(1-tax),
                                                4)
                    else:
                        fdata[i][1] = round(fdata[i][1] / dau[i], 4)
                else:
                    fdata[i][1] = 0
            data = fdata

        return data

    def get_few_kpi(self, factor_lst, with_date=True, per_user=False,
                    currency=None, params=None, tax=None):
        """ Request data for few different KPI factors

        :rtype: :class:`list`
        """

        params = params or dict(self.defaults)  # request params
        if currency:
            params['currency'] = currency  # cash, coins, etc...

        if per_user:
            get_func = self.get_kpi_dau
        else:
            get_func = self.get_kpi

        count_index = 0
        results = []
        for factor in factor_lst:
            if count_index == 0:

                if with_date:
                    results = get_func(factor, tax=tax)
                else:
                    results = [[i] for i in get_func(factor, False, tax=tax)]
                count_index += 1

            else:  # > 0
                data = get_func(factor, False, tax=tax)
                for i in range(len(data)):
                    results[i] += [data[i]]

        return results

    def get_evt_lst(self, params=None):
        """
        Request list with all events from swrve

        :rtype: :class:`list`
        """

        # Request url
        url = 'https://dashboard.swrve.com/api/1/exporter/event/list'
        params = params or dict(self.defaults)  # request params

        req = requests.get(url, params=params).json()  # do request
        # Request errors
        if isinstance(req, dict):
            if 'error' in req.keys():
                print('Error: %s' % req['error'])
                return

        return req

    def get_payload_lst(self, ename=None, params=None):
        """
        Request payloads list for event

        :rtype: :class:`list`
        """

        # Request url
        url = 'https://dashboard.swrve.com/api/1/exporter/event/payloads'
        params = params or dict(self.defaults)  # request params
        if ename:
            params['name'] = ename

        req = requests.get(url, params=params).json()  # do request
        # Request errors
        if isinstance(req, dict):
            if 'error' in req.keys():
                print('Error: %s' % req['error'])
                return

        return req

    def get_evt_stat(self, ename=None, payload=None, payload_val=None,
                     payload_sum=None, with_date=True, per_user=False,
                     params=None):
        """ Request events triggering count with(out) payload key.
        If with payload, keys are payload's values, else key is an event name.

        :rtype: :class:`dict`
        """

        if (payload_val or payload_sum) and not payload:
            print('\
If you use payload value or sum then you need to set payload too')
            return

        params = params or dict(self.defaults)  # request params
        if ename:
            params['name'] = ename
        if payload:
            params['payload_key'] = payload

        if payload:
            url = 'https://dashboard.swrve.com/api/1/exporter/event/payload'
        else:
            url = 'https://dashboard.swrve.com/api/1/exporter/event/count'

        req = requests.get(url, params=params).json()  # do request
        # Request errors
        if isinstance(req, dict):
            if 'error' in req.keys():
                print('Error: %s' % req['error'])
                return

        data = {}
        if payload and payload_val:
            payload_val = str(payload_val)
            for d in req:
                if d['payload_value'] == payload_val:
                    data[payload_val] = d['data']
                    break

        elif payload:  # with payload
            for d in req:
                if with_date:  # key is a payload value
                    data[d['payload_value']] = d['data']
                else:
                    data[d['payload_value']] = [i[1] for i in d['data']]

        else:  # without payload key is an event name
            if not with_date:
                data[req[0]['name']] = [i[1] for i in req[0]['data']]
            else:
                data[req[0]['name']] = req[0]['data']

            if per_user:  # calc for one user
                dau = self.get_kpi('dau', False, params=params)
                key = list(data.keys())[0]  # one element => first key
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

        # Aggregate payload values
        if payload and payload_sum:
            for key in data:
                val = 0
                if not with_date:
                    for i in data[key]:
                        val += i
                else:
                    for i in data[key]:
                        val += i[1]

                data[key] = val

        return data

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
        """ Get List of all segments

        :rtype: :class:`list`
        """

        # Request url
        url = 'https://dashboard.swrve.com/api/1/exporter/segment/list'
        params = params or dict(self.defaults)  # request params

        req = requests.get(url, params=params).json()  # do request
        # Request errors
        if isinstance(req, dict):
            if 'error' in req.keys():
                print('Error: %s' % req['error'])
                return

        return req
