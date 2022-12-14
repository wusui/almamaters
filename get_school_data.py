#!/usr/bin/python
# Copyright (c) 2022 Warren Usui
# This code is licensed under the MIT license (see LICENSE for details)
"""
Generate reports from ESPN data
"""
import json
from functools import reduce
import pandas as pd

def read_league(league):
    """ Read file created by get_player_info """
    with open(f"{league}.json", "r", encoding='utf8') as infile:
        return json.load(infile)

def doaccum(player_data):
    """ Add new player to this school structure """
    def doaccum_lev2(accum):
        def doaccum_lev3(schinfo):
            if schinfo == player_data['School']:
                return [schinfo, accum[schinfo] + [player_data]]
            return [schinfo, accum[schinfo]]
        return doaccum_lev3
    return doaccum_lev2

def extract_all(accum, player_data):
    """ Update school information or add a new school entry """
    if player_data['School'] in accum:
        return dict(list(map(doaccum(player_data)(accum), accum.keys())))
    return accum | {player_data['School']: [player_data]}

def get_school_keys(school_data):
    """ Return school information and associated keys """
    def inner_skeys():
        return [school_data, [*school_data]]
    return inner_skeys

def count_school_keys(skey_data):
    """ Extract list of schools and their associated number of players """
    def comb_sch_cnt_keys(school):
        return f'{(500 - len(skey_data[0][school])):03d}^{school}'
    def inner_count_keys():
        return [skey_data, sorted(list(map(comb_sch_cnt_keys, skey_data[1])))]
    return inner_count_keys

def get_table_info(league):
    """ Reduce player records to list of school counts and lists of players
        at a school """
    return count_school_keys(get_school_keys(
            reduce(extract_all, read_league(league), {}))())()

def merge_cols(prev_dict, new_info):
    """ Return new column data for updated fields (used by DataFrame
        related code) """
    return {"Name": prev_dict["Name"] + [new_info['Name']],
            "Pos":  prev_dict["Pos"] + [new_info['Pos']],
            "Team": prev_dict["Team"] + [new_info['Team']]}

def mk_solid(school):
    """ Break up dash usage in webpage school names """
    return '-'.join(school.split())

def get_html_name(schlg):
    """ Format school/league related html name """
    return f"{schlg[1]}_{mk_solid(schlg[0])}.html"

def gen_df_table(schlg):
    """ Write school related data to an html file """
    def gen_df_inner(data_out):
        with open(get_html_name(schlg), "w", encoding='utf8') as out_file:
            out_file.write(pd.DataFrame(
                    reduce(merge_cols, data_out[schlg[0]],
                            {"Name": [], "Pos": [], "Team": []})
            ).to_html(index=False))
    return gen_df_inner

def do_report(expanded_info):
    """ Wrap output of school report """
    def do_rpt_inner(schlg):
        gen_df_table(schlg)(expanded_info[0][0])
    return do_rpt_inner

def make_report_school(league, school):
    """ Generate an html page of players at a school """
    return do_report(get_table_info(league))([school, league])

def xtract_numb(cmb_val):
    """ Convert player count stored in second part of extracted data into a
        more reasonable number """
    return 500 - int(cmb_val.split("^")[0])

def add_sc_rec(accum, new_rec):
    """ Accumulate values in columns used by the DataFrame that displays
        player numbers at each school """
    return {"Number": accum["Number"] + [xtract_numb(new_rec)],
            "College": accum["College"] + [new_rec.split("^")[-1]]}

def make_report_dist(league):
    """ Generate report of player numbers from specific schools """
    with open(f"{league}_school_dist.html", "w", encoding='utf8') as out_file:
        out_file.write(pd.DataFrame(
                    reduce(add_sc_rec, get_table_info(league)[1],
                            {"Number": [], "College": []})
        ).to_html(index=False))

if __name__ == "__main__":
    make_report_school("nfl", "UCLA")
    make_report_dist("nfl")
    make_report_school("nba", "UCLA")
    make_report_dist("nba")
