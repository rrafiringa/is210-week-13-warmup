#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" City Inspection grading module """

import json


GSCALE = {'A': 1.00,
          'B': 0.90,
          'C': 0.80,
          'D': 0.70,
          'F': 0.60}


def get_score_summary(infile):
    """
    Inspection score summary
    Args:
        infile (File): Input CSV file
    Returns:
        dict: Dictionary, keyed by boro, whose value is a tuple
        with the number of restaurateurs per boro (who have scores),
        and the average score (as a float) for that boro.
    Examples:
        >>> get_score_summary('inspection_results.csv')
        >>> {'BRONX': (156, 0.9762820512820514),
             'BROOKLYN': (417, 0.9745803357314141),
             'STATEN ISLAND': (46, 0.9804347826086955),
             'MANHATTAN': (748, 0.9771390374331531),
             'QUEENS':(414, 0.9719806763285017)}
    """
    res = {}
    try:
        with open(infile, 'r') as indata:
            header = tuple(indata.readline().rstrip().split(','))
            oldid = ''
            deduped = []
            for line in indata:
                # Get record
                record = dict(zip(header, tuple(line.rstrip().split(','))))
                # Deduplicate
                currid = record['CAMIS']
                if currid == oldid \
                    or record['GRADE'].strip().upper() \
                        not in GSCALE.keys():
                    continue
                else:
                    oldid = currid
                deduped += [{'CAMIS': record['CAMIS'],
                             'BORO': record['BORO'],
                             'GRADE': record['GRADE']}]
            # Transform
            tmpdata = {'BRONX': (0, 0.0),
                       'BROOKLYN': (0, 0.0),
                       'QUEENS': (0, 0.0),
                       'MANHATTAN': (0, 0.0),
                       'STATEN ISLAND': (0, 0.0)}

            for rec in deduped:
                idx = rec['BORO']
                total = tmpdata[idx][0] + 1
                gaccum = tmpdata[idx][1] + GSCALE[rec['GRADE']]
                average = float(gaccum / total)
                tmpdata[idx] = (total, gaccum)
                res[idx] = (total, average)

    except IOError:
        print 'Could not open ' + infile

    else:
        return res


def get_market_density(infile):
    """
    Calculates market density per borough
    Args:
        infile (File): json input file
    Returns:
        dict: Number of green markets per borough
    Examples:
        >>> get_market_density('green_markets.json')
        >>> {u'BRONX': 32, u'BROOKLYN': 48, u'STATEN ISLAND': 2,
             u'MANHATTAN': 39, u'QUEENS': 16}
    """

    try:
        res = {}
        with open(infile, 'r') as jsonfile:
            table = json.load(jsonfile)
            cols = [fields['fieldName']
                    for fields in table['meta']['view']['columns']]
            rows = table['data']
            table = [dict(zip(cols, row)) for row in rows]
            for row in table:
                idx = row['borough'].strip().upper()
                if idx in res.keys():
                    res[idx] += 1
                else:
                    res[idx] = 1

    except IOError:
        print 'Could not open ' + infile

    else:
        return res


def correlate_data(in_csv, in_json, out_json):
    """
    Find ratio of green market per restorateurs and score
    Args:
        in_csv (File): csv input file
        in_json (File): json input file
        out_json (File): Output json file
    Returns:
        File: Output results to json
    Examples:
        >>> correlate_data('file1.csv', 'file2.json', file3.json)
        >>> {'BRONX': (0.9762820512820517, 0.20512820512820512),
             'BROOKLYN': (0.9745803357314147, 0.11510791366906475),
             'STATEN ISLAND': (0.9804347826086957, 0.043478260869565216),
             'MANHATTAN': (0.9771390374331524, 0.05213903743315508),
             'QUEENS': (0.9719806763285018, 0.03864734299516908)}
    """
    restos = get_score_summary(in_csv)
    markets = get_market_density(in_json)
    try:
        res = {}
        with open(out_json, 'w') as outfile:
            for key in restos.keys():
                res[key] = (restos[key][1], float(markets[key])
                            / restos[key][0])

            json.dump(res, outfile)

    except IOError:
        print 'Could not open ' + outfile + ' for writing.'

    else:
        return res


if __name__ == '__main__':
    print get_score_summary('inspection_results.csv')
    print '========================================='
    print get_market_density('green_markets.json')
    print '========================================='
    print correlate_data('inspection_results.csv',
                         'green_markets.json',
                         'correlated.json')