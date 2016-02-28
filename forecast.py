#!/usr/bin/env python3
"""
Source: https://github.com/pavdmyt/apis
"""
import argparse
import logging
import json
import os
import pprint
import time

import urllib.request as urequest
import urllib.parse as uparse


# Put your Forecast.io api key here, otherwise provide it via
# --api-key argument.
API_KEY = ''


class Coordinates:
    """Coordinates of some locations."""
    kyiv = (50.45, 30.523333)
    lutsk = (50.75, 25.335833)


class ForecastAPI:
    """Simple implementation of Forecast.io API.

    https://developer.forecast.io/docs/v2 - API documentation.
    """
    _base_url = 'https://api.forecast.io/forecast'

    def __init__(self, api_key):
        self.api_key = api_key
        self.params = {}

    def get_forecast(self, coordinates, units='auto', save_as_file=None):
        # Latitude and Longtitude.
        lat, lon = map(str, coordinates)
        self.params['units'] = units

        # Compose request.
        enc_params = uparse.urlencode(self.params)
        full_url = "{0}/{1}/{2},{3}?{4}".format(self._base_url, self.api_key,
                                                lat, lon, enc_params)
        req = urequest.Request(full_url)

        # Send request.
        try:
            with urequest.urlopen(req) as resp:
                fetched_data = resp.read()
        except Exception as e:
            print("\n* Error occured: {}\n".format(e))

        # Write to file.
        if isinstance(save_as_file, str):
            try:
                with open(save_as_file, 'wb') as fp:
                    fp.write(fetched_data)
            except Exception as e:
                print("\n* Error occured: {}\n".format(e))

        return json.loads(fetched_data.decode())

    def load_from_file(self, file_name):
        """Loads forecast data from the given file.

        Returns dict.
        """
        try:
            with open(file_name, 'r') as fp:
                return json.loads(fp.read())
        except Exception as e:
            print("\n* Error occured: {}\n".format(e))


# === Helper functions ===

def print_current(data_dict):
    pass


def parse_daily_data(data_list):
    # `apparentTemperatureMax`
    temp_data = []
    for day in data_list:
        temp = day.get('apparentTemperatureMax')
        temp_data.append(temp)
        if temp is None:
            date_str = time.ctime(day.get('time'))
            logging.warn(" `apparentTemperatureMax` data for `{}` is missing."
                         .format(date_str))
    return temp_data


def parse_args(api_key):
    """CLI interface."""
    required = not bool(api_key)
    descr = ("This script uses weather data provided by the Dark Sky "
             "Forecast API to show current weather conditions and forecasts "
             "in the form of bar charts.")

    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument('mode',
                        choices=['current', 'daily'],
                        help='Output mode: `current` or `daily`')
    parser.add_argument('--api-key',
                        required=required,
                        help='API key provided by Forecast.io')
    parser.add_argument('--data-file',
                        help=('Path to the file containing the Forecast data '
                              '(also acts as target file if the data has to '
                              'be downloaded first).')
                        )
    opts = parser.parse_args()
    return opts


def main():
    opts = parse_args(API_KEY)
    logging.basicConfig(level=logging.INFO)

    # API init.
    if API_KEY:
        api = ForecastAPI(API_KEY)
    else:
        api = ForecastAPI(opts.api_key)

    # Handle `--data-file` argument.
    if isinstance(opts.data_file, str):
        if os.path.exists(opts.data_file):
            fdata = api.load_from_file(opts.data_file)
        else:
            fdata = api.get_forecast(Coordinates.kyiv,
                                     save_as_file=opts.data_file)
    else:
        fdata = api.get_forecast(Coordinates.kyiv)

    # Handle `mode`. `else:` handled by argument parser.
    if opts.mode == 'current':
        res = fdata.get('currently')
    elif opts.mode == 'daily':
        daily_data = fdata.get('daily')
        res = parse_daily_data(daily_data.get('data'))

    # Print result.
    pp = pprint.PrettyPrinter()
    pp.pprint(res)


if __name__ == '__main__':
    main()
