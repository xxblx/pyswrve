# -*- coding: utf-8 -*-


class SwrveApiException(Exception):
    __slots__ = ['error', 'code', 'request_params', 'request_url']

    def __init__(self, error, code, request_params, request_url):
        super().__init__()

    def __str__(self):
        # TODO
        pass
