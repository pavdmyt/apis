#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A client for Ergast API.
Source: https://github.com/pavdmyt/apis
"""
import requests


# TODO: add CLI interface.
# TODO: add pretty printing of result tables.
# TODO: add caching.

# === API part ===

def _url(path, resp_format='json'):
    """Base URL for Ergast API.

    API Documentation - http://ergast.com/mrd/
    """
    base = 'http://ergast.com/api/f1/current{0}.{1}'
    return base.format(path, resp_format)


def get_cur_driver_standings():
    """Get driver standings for the current season."""
    return requests.get(_url('/driverStandings'))


def get_cur_constructor_standings():
    """Get constructor standings for the current season."""
    return requests.get(_url('/constructorStandings'))


def get_cur_schedule():
    """Get race schedule for the current season."""
    return requests.get(_url(''))


def get_cur_race_res():
    """Get results from the most recent race."""
    return requests.get(_url('/last/results'))


def get_cur_quali_res():
    """Get most recent qualifying results."""
    return requests.get(_url('/last/qualifying'))


# === Parsers ===

def parse_schedule(resp_json):
    """Parse race schedule (calendar).

    Return table (list) with rows (tuples) of parsed data.
    """
    schedule = resp_json['MRData']['RaceTable']['Races']

    table = []
    for item in schedule:
        season = item['season']
        round = item['round']
        rname = item['raceName']
        date = item['date']
        time = item['time']
        # 'Circuit' obj.
        circuit = item['Circuit']
        cname = circuit['circuitName']
        loc = circuit['Location']['locality']
        country = circuit['Location']['country']
        row = (season, round, rname, date, time, cname, loc, country)
        table.append(row)
    return table


def parse_constructor_standings(resp_json):
    """Parse standings in constructors championship.

    Return table (list) with rows (tuples) of parsed data.
    """
    data = resp_json['MRData']['StandingsTable']['StandingsLists'][0]  # meta
    standings = data['ConstructorStandings']

    table = []
    for item in standings:
        pos = item['position']
        points = item['points']
        wins = item['wins']
        # 'Constructor' obj.
        constr = item['Constructor']
        cname = constr['name']
        nationality = constr['nationality']
        row = (pos, cname, nationality, points, wins)
        table.append(row)
    return table


def parse_driver_standings(resp_json):
    """Parse standings in drivers championship.

    Return table (list) with rows (tuples) of parsed data.
    """
    data = resp_json['MRData']['StandingsTable']['StandingsLists'][0]  # meta
    standings = data['DriverStandings']

    table = []
    for item in standings:
        pos = item['position']
        points = item['points']
        wins = item['wins']
        # 'Driver' obj.
        driver = item['Driver']
        dname = '{0} {1}'.format(driver['givenName'], driver['familyName'])
        # 'Constructors' obj in list.
        constr = item['Constructors'][0]
        cname = constr['name']
        row = (pos, dname, cname, points, wins)
        table.append(row)
    return table


def parse_rase_results(resp_json):
    """Parse results of the most recent race.

    Return table (list) with rows (tuples) of parsed data.
    """
    data = resp_json['MRData']['RaceTable']['Races'][0]  # meta
    results = data['Results']

    table = []
    for item in results:
        pos = item['position']
        num = item['number']
        laps = item['laps']
        grid = item['grid']
        status = item['status']
        points = item['points']
        # 'Driver' obj.
        driver = item['Driver']
        dname = '{0} {1}'.format(driver['givenName'], driver['familyName'])
        # 'Constructor' obj.
        constr = item['Constructor']
        cname = constr['name']
        # 'Time' obj.
        try:  # Time info is not available for all items.
            time = item['Time']['time']
        except KeyError:
            time = ''
        row = (pos, num, dname, cname, laps, grid, time, status, points)
        table.append(row)
    return table


def parse_quali_results(resp_json):
    """Parse most recent qualifying results.

    Return table (list) with rows (tuples) of parsed data.
    """
    data = resp_json['MRData']['RaceTable']['Races'][0]  # meta
    results = data['QualifyingResults']

    table = []
    for item in results:
        pos = item['position']
        num = item['number']
        q1 = item['Q1']
        q2 = item.get('Q2', '')  # Not available for all items.
        q3 = item.get('Q3', '')  # Not available for all items.
        # 'Driver' obj.
        driver = item['Driver']
        dname = '{0} {1}'.format(driver['givenName'], driver['familyName'])
        # 'Constructor' obj.
        constr = item['Constructor']
        cname = constr['name']
        row = (pos, num, dname, cname, q1, q2, q3)
        table.append(row)
    return table


def main():
    pass


if __name__ == '__main__':
    # === Don't pull API too much! ===
    # d_stand = get_cur_driver_standings().json()
    # c_stand = get_cur_constructor_standings().json()
    # sch = get_cur_schedule().json()
    # race_res = get_cur_race_res().json()
    # quali_res = get_cur_quali_res().json()
    pass
