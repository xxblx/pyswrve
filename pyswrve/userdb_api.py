# -*- coding: utf-8 -*-

import os
from urllib.parse import urljoin, urlsplit
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from .api import SwrveApi
from .exceptions import SwrveApiException


class SwrveUserdbApi(SwrveApi):
    """
    Class for requesting and downloading UserDB with Swrve Export API

    https://docs.swrve.com/swrves-apis/non-client-apis/\
swrve-export-api-guide/#User_DB_Export
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
        self._api_url = urljoin(self._api_url, 'userdbs.json')

    def get_urls(self):
        """ Request urls list for UserDB download

        :return: [:class:`dict`] dict with urls for data files, schemas
        """

        return self.send_api_request(self._api_url)

    def download_data(self, path, exclude_data=False, exclude_schemas=False,
                      workers=5):
        """ Download UserDB

        :param path: [:class:`str`]path to base directory where userdb
            will be stored
        :param exclude_data: [`bool`] if True method doesn't download
            data files
        :param exclude_schemas: [`bool`] if True method doesn't download
            db schemas
        :param workers: [:class:`int`] count of workers for downloading
        :return: [:class:`list`] list of downloaded files
        """

        urls_dct = self.get_urls()

        date_dir = os.path.join(path, urls_dct['date'])
        downloaded_data = []

        if not exclude_data:
            pass

        if not exclude_schemas:
            schemas_dir = os.path.join(date_dir, 'schemas')
            os.makedirs(schemas_dir)
            results = self.download_urls(
                schemas_dir,
                urls_dct['schemas'].values(),
                workers=workers
            )
            downloaded_data += results

        if not exclude_data:
            for section in urls_dct['data_files']:
                section_dir = os.path.join(date_dir, 'data', section)
                os.makedirs(section_dir)
                results = self.download_urls(
                    schemas_dir,
                    urls_dct['data_files'].values(),
                    workers=workers
                )
                downloaded_data += results

        return downloaded_data

    def download_urls(self, download_dir, urls, workers=5):
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_path = [
                executor.submit(self.download_file, download_dir, url)
                for url in urls
            ]

            results = [
                future.result()
                for future in as_completed(future_to_path)
            ]

        return results

    def download_file(self, download_dir, url):
        fname = os.path.basename(urlsplit(url).path)
        save_path = os.path.join(download_dir, fname)

        res = requests.get(url, params=self._params, stream=True)
        if res.status_code != 200:
            error = None
            try:
                error['error'] = res.json()['error']
            except ValueError:
                pass
            raise SwrveApiException(error, res.status_code, url, self._params)

        with open(save_path, 'wb') as f:
            for i in res.iter_content(chunk_size=1024):
                if i:
                    f.write(i)
                    f.flush()

        return save_path
