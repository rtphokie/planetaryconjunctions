import os
from datetime import date, timedelta
from itertools import combinations
from os.path import expanduser

import pandas as pd
from skyfield import api
from skyfield.searchlib import find_minima

eph = None
ts = api.load.timescale()


def separation(t, b1name, b2name):
    e = eph['earth'].at(t)
    b1a = e.observe(eph[b1name]).apparent()
    b2a = e.observe(eph[b2name]).apparent()
    return b1a.separation_from(b2a).degrees


def separation_mercury_venus(t):
    return separation(t, 'MERCURY', 'VENUS')


def separation_mercury_moon(t):
    return separation(t, 'MERCURY', 'MOON')


def separation_mercury_mars(t):
    return separation(t, 'MERCURY', 'MARS')


def separation_mercury_jupiter(t):
    return separation(t, 'MERCURY', 'JUPITER BARYCENTER')


def separation_mercury_saturn(t):
    return separation(t, 'MERCURY', 'SATURN BARYCENTER')


def separation_venus_moon(t):
    return separation(t, 'VENUS', 'MOON')


def separation_venus_mars(t):
    return separation(t, 'VENUS', 'MARS')


def separation_venus_jupiter(t):
    return separation(t, 'VENUS', 'JUPITER BARYCENTER')


def separation_venus_saturn(t):
    return separation(t, 'VENUS', 'SATURN BARYCENTER')


def separation_moon_mars(t):
    return separation(t, 'MOON', 'MARS')


def separation_moon_jupiter(t):
    return separation(t, 'MOON', 'JUPITER BARYCENTER')


def separation_moon_saturn(t):
    return separation(t, 'MOON', 'SATURN BARYCENTER')


def separation_mars_jupiter(t):
    return separation(t, 'MARS', 'JUPITER BARYCENTER')


def separation_mars_saturn(t):
    return separation(t, 'MARS', 'SATURN BARYCENTER')


def separation_jupiter_saturn(t):
    return separation(t, 'JUPITER BARYCENTER', 'SATURN BARYCENTER')


def main(datadir=None, ephfilename='de421.bsp', min_sep=5, year=2022, days=7):
    df_sep, df_minima = calculate(datadir=datadir, ephfilename=ephfilename, year=year)
    # print(df_sep)
    # print(df_minima)

    start = date.today()
    end = start + timedelta(days=days)
    print(start)
    print(end)
    df = df_sep[(df_sep.date >= str(start)) & (df_sep.date <= str(end))]
    print(df)
    for n, row in df.iterrows():
        print(row)


def calculate(datadir=None, ephfilename='de421.bsp', year=2022):
    global eph
    datadir = config(datadir)
    load = api.Loader(datadir)
    eph = load(ephfilename)
    eph_start, eph_end = ephemeris_coverage(eph)

    fs = {
        'mercury': {'venus': separation_mercury_venus, 'moon': separation_mercury_moon, 'mars': separation_mercury_mars,
                    'jupiter': separation_mercury_jupiter, 'saturn': separation_mercury_saturn},
        'venus': {'moon': separation_venus_moon, 'mars': separation_venus_mars, 'jupiter': separation_venus_jupiter,
                  'saturn': separation_venus_saturn},
        'moon': {'mars': separation_moon_mars, 'jupiter': separation_moon_jupiter, 'saturn': separation_moon_saturn},
        'mars': {'jupiter': separation_mars_jupiter, 'saturn': separation_mars_saturn},
        'jupiter': {'saturn': separation_jupiter_saturn}}

    arr = ['mercury', 'venus', 'moon', 'mars', 'jupiter', 'saturn']
    csv_filename = f'planetary_separations_{year}.csv'
    try:
        df_sep = pd.read_csv(csv_filename)
    except:
        data_sep = {}
        for comb in list(combinations(arr, 2)):
            f = fs[comb[0]][comb[1]]
            f.step_days = 1.0
            times = ts.utc(year, 1, range(1, 366))
            separations = f(times)
            for t, elongation_degrees in zip(times, separations):
                datestr = t.utc_strftime('%Y-%m-%d')
                if datestr not in data_sep.keys():
                    data_sep[datestr] = {}
                data_sep[datestr][f"{comb[0]}-{comb[1]}"] = round(elongation_degrees, 2)
        df_sep = pd.DataFrame.from_dict(data_sep, orient='index')
        df_sep.to_csv(csv_filename, index_label='date')

    csv_filename = f'planetary_separation_minima_{eph_start.year}-{eph_end.year}.csv'
    try:
        df_minima = pd.read_csv(csv_filename)
    except:
        t0 = ts.from_datetime(eph_start)
        t1 = ts.from_datetime(eph_end)
        data_minima = {}
        for comb in list(combinations(arr, 2)):
            f = fs[comb[0]][comb[1]]
            f.step_days = 1.0
            times, elongations = find_minima(t0, t1, f)
            for t, elongation_degrees in zip(times, elongations):
                datestr = t.utc_strftime('%Y-%m-%d')
                if datestr not in data_minima.keys():
                    data_minima[datestr] = {}
                # print(f"{t.utc_strftime()}  {elongation_degrees:4.1f}°")
                data_minima[datestr][f"{comb[0]}-{comb[1]}"] = round(elongation_degrees, 2)
        df_minima = pd.DataFrame.from_dict(data_minima, orient='index')
        df_minima.to_csv(csv_filename, index_label='date')

    return df_sep, df_minima


def ephemeris_coverage(eph):
    '''
    Extract the start and end of the time period covered by the spice file
    '''
    ephrange = ts.tt_jd(range(round(eph.spk.pairs[0, 1].start_jd + 1.5), round(eph.spk.pairs[0, 1].end_jd - 1.5)))
    eph_start = ephrange[0].utc_datetime()
    eph_end = ephrange[-1].utc_datetime()
    return eph_start, eph_end


def load_ephemeris(datadir, filename):
    load = api.Loader(datadir)
    return load(filename)


def config(datadir):
    if datadir is None:
        # find the first directory in the list that exists, otherwise use the last one
        # Skyfield will create it if it does not exist
        dirs = ['/var/data', f"{expanduser('~')}/.data"]
        datadir = dirs[-1]
        for dir_path in dirs:
            if dir_path != dirs[-1]:
                datadir = _direxists(dir_path)
    else:
        datadir = _direxists(datadir)
        if datadir is None:
            raise NotADirectoryError(f"{datadir} not found")
    return datadir


def _direxists(dir):
    # checks for existence of named directory, returns that directory if it exists, None otherwise.
    isdir = os.path.isdir(dir)
    if isdir:
        return dir
    else:
        return None
