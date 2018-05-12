# -*- coding: utf-8 -*-


class SwrveApiException(Exception):
    __slots__ = ['error', 'status_code', 'request_url', 'request_params']

    def __init__(self, error, status_code, request_url, request_params):
        super().__init__()
        self.error = error
        self.status_code = status_code
        self.request_url = request_url
        self.request_params = request_params

    def __str__(self):
        msg = '{self.status_code}, {self.error}, url: {self.request_url}, \
params: {self.request_params}'.format(self=self)
        return msg
