#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''F1 info. Client for Ergast API (http://ergast.com/mrd/).

Usage:
    ergast_api.py cal
    ergast_api.py stand (driver | constructor)
    ergast_api.py res (race | quali)
    ergast_api.py -h | --help

Arguments:
    cal             Race calendar for the current season.
    stand           Standings in the driver or constructor championships.
    res             Most recent race or qualifying results.

Options:
    -h --help       Show this screen.

'''
import requests

from docopt import docopt
from tabulate import tabulate


# TODO: add metadata to result tables.
# TODO: add check of Internet connection.
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


def parse_race_results(resp_json):
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
    args = docopt(__doc__)

    if args['cal']:
        resp_json = get_cur_schedule().json()
        table = parse_schedule(resp_json)
        headers = ("Season", "Round", "Race Name", "Date", "Time", "Circuit",
                   "Locality", "Country")

    if args['stand'] and args['driver']:
        resp_json = get_cur_driver_standings().json()
        table = parse_driver_standings(resp_json)
        headers = ("Pos", "Driver", "Constructor", "Points", "Wins")

    if args['stand'] and args['constructor']:
        resp_json = get_cur_constructor_standings().json()
        table = parse_constructor_standings(resp_json)
        headers = ("Pos", "Constructor", "Nationality", "Points", "Wins")

    if args['res'] and args['race']:
        resp_json = get_cur_race_res().json()
        table = parse_race_results(resp_json)
        headers = ("Pos", "No", "Driver", "Constructor", "Laps", "Grid",
                   "Time", "Status", "Points")

    if args['res'] and args['quali']:
        resp_json = get_cur_quali_res().json()
        table = parse_quali_results(resp_json)
        headers = ("Pos", "No", "Driver", "Constructor", "Q1", "Q2", "Q3")

    print(tabulate(table, headers=headers, tablefmt='fancy_grid'))


if __name__ == '__main__':
    main()
