#!/usr/bin/env python3
"""
A CLI tool to shorten URLs using Bitly API
Source: https://github.com/pavdmyt/apis
"""
import argparse
import logging

import urllib.request as urequest
import urllib.parse as uparse
from urllib.error import HTTPError


# Put your Bitly token here, otherwise provide it via
# --api-token argument.
TOKEN = ''


class BitlyAPI:
    """Simple implementation of Bitly API.

    http://dev.bitly.com/documentation.html - API documentation.
    """
    _base_url = 'https://api-ssl.bitly.com'

    def __init__(self, access_token):
        self.access_token = access_token
        self.params = {'access_token': access_token}

    def shorten(self, long_url, format='txt'):
        """Shorten given URL.

        Implementation of /v3/shorten method.
        """
        if not validate_url(long_url):
            return

        # Set params.
        method = '/v3/shorten'
        self.params['longUrl'] = long_url
        self.params['format'] = format

        # Encode params.
        enc_params = uparse.urlencode(self.params)
        get = method + '?' + enc_params
        req = urequest.Request(self._base_url + get)

        # Send request.
        try:
            with urequest.urlopen(req) as resp:
                short_url = resp.read()
                return short_url.decode().rstrip()
        except Exception as e:
            print("\n* Error occured: {}\n".format(e))


# === Helper functions ===

def validate_url(url):
    """Checks that given url is a valid URL."""
    try:
        with urequest.urlopen(url) as test:
            return True
    except HTTPError as e:
        if e.getcode() == 403:
            logging.warn(" web server returned '403 Forbidden'")
            return True
        print("\n* Error occured: {}".format(e))
    except Exception as e:
        print("\n* Error occured: {}".format(e))


def parse_args(api_token):
    """CLI interface."""
    required = not bool(api_token)

    parser = argparse.ArgumentParser()
    parser.add_argument('long_url',
                        help='URL to shorten')
    parser.add_argument('--api-token',
                        required=required,
                        help='API token provided by bit.ly')
    opts = parser.parse_args()
    return opts


def main():
    opts = parse_args(TOKEN)
    logging.basicConfig(level=logging.INFO)

    # API init.
    if TOKEN:
        api = BitlyAPI(TOKEN)
    else:
        api = BitlyAPI(opts.api_token)

    # Result.
    result = api.shorten(opts.long_url)
    if result:
        print("\n{}".format(result))


if __name__ == '__main__':
    main()
