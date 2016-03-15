#!/usr/bin/env python
"""
A CLI tool to shorten URLs using Bitly API
Source: https://github.com/pavdmyt/apis
"""
import argparse
import errno
import json
import os
import sys

from contextlib import closing

try:
    import urllib2 as urequest
    import urllib as uparse
except ImportError:
    import urllib.request as urequest
    import urllib.parse as uparse

# Put your Bitly token here, otherwise provide it via
# --api-token argument.
TOKEN = ''

XDG_CACHE_DIR = os.environ.get('XDG_CACHE_HOME',
                               os.path.join(os.path.expanduser('~'), '.cache'))
CACHE_FILE = os.path.join(XDG_CACHE_DIR, 'urlshort_cache.json')


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
            with closing(urequest.urlopen(req)) as resp:
                short_url = resp.read()
                return short_url.decode().rstrip()
        except Exception as e:
            print("\n* Error occured while communicating with Bitly: {}\n"
                  .format(e))


# === Helper functions ===

def validate_url(url):
    """Checks that given url is a valid URL."""
    try:
        req = urequest.Request(url)
        if sys.version < '3':
            req.get_host()
        return True
    except ValueError as e:
        print("\n* Error occured while validating given URL: {}".format(e))


def internet_on():
    """Checks that internet connection is available."""
    remote = 'http://google.com'
    try:
        with closing(urequest.urlopen(remote)) as test:
            return True
    except Exception as e:
        print("\n* Error occured while checking internet connection: {}\n"
              .format(e))


def load_cache():
    """Loads cached data from JSON file into the dict."""
    with open(CACHE_FILE, 'r') as fp:
        return json.load(fp)


def write_cache(cache_dct):
    """Write cache dict to JSON."""
    with open(CACHE_FILE, 'w') as fp:
        json.dump(cache_dct, fp)


def parse_args(api_token):
    """CLI interface."""
    descr = "This script uses Bitly API to shorten given URLs."

    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument('long_url',
                        help='URL to shorten')
    if not TOKEN:
        parser.add_argument('--api-token',
                            required=True,
                            help='API token provided by bit.ly')
    opts = parser.parse_args()
    return opts


def main():
    if not internet_on():
        print("* Failed to establish network connection.")
        return
    opts = parse_args(TOKEN)

    # API init.
    if TOKEN:
        api = BitlyAPI(TOKEN)
    else:
        api = BitlyAPI(opts.api_token)

    # Load cache.
    try:
        cached_data = load_cache()
    except IOError as e:
        if e.errno == errno.ENOENT:
            print('\n* The file "{0}" does not exist: creating it.'
                  .format(CACHE_FILE))
            open(CACHE_FILE, 'a').close()
            cached_data = {}

    # Result.
    if opts.long_url in cached_data:
        result = cached_data[opts.long_url]
    else:
        result = api.shorten(opts.long_url)
        cached_data[opts.long_url] = result
        write_cache(cached_data)

    if result:
        print("\n{}".format(result))


if __name__ == '__main__':
    main()
