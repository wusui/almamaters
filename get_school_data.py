import json
from functools import reduce
import pandas as pd

def read_league(league):
    with open(f"{league}.json", "r", encoding='utf8') as infile:
        return json.load(infile)

def doaccum(player_data):
    def doaccum_lev2(accum):
        def doaccum_lev3(schinfo):
            if schinfo == player_data['School']:
                return [schinfo, accum[schinfo] + [player_data]]
            return [schinfo, accum[schinfo]]
        return doaccum_lev3
    return doaccum_lev2

def extract_all(accum, player_data):
    if player_data['School'] in accum:
        return dict(list(map(doaccum(player_data)(accum), accum.keys())))
    return accum | {player_data['School']: [player_data]}

def get_school_keys(school_data):
    def inner_skeys():
        return [school_data, [*school_data]]
    return inner_skeys

def count_school_keys(skey_data):
    def comb_sch_cnt_keys(school):
        return f'{(500 - len(skey_data[0][school])):03d}^{school}'
    def inner_count_keys():
        return [skey_data, sorted(list(map(comb_sch_cnt_keys, skey_data[1])))]
    return inner_count_keys

def get_table_info(league):
    return count_school_keys(get_school_keys(
            reduce(extract_all, read_league(league), {}))())()

def merge_cols(prev_dict, new_info):
    return {"Name": prev_dict["Name"] + [new_info['Name']],
            "Pos":  prev_dict["Pos"] + [new_info['Pos']],
            "Team": prev_dict["Team"] + [new_info['Team']]}

def mk_solid(school):
    return '-'.join(school.split())

def get_html_name(schlg):
    return f"{schlg[1]}_{mk_solid(schlg[0])}.html"

def gen_df_table(schlg):
    def gen_df_inner(data_out):
        with open(get_html_name(schlg), "w", encoding='utf8') as out_file:
            out_file.write(pd.DataFrame(
                    reduce(merge_cols, data_out[schlg[0]],
                            {"Name": [], "Pos": [], "Team": []})
            ).to_html(index=False))
    return gen_df_inner

def do_report(expanded_info):
    def do_rpt_inner(schlg):
        gen_df_table(schlg)(expanded_info[0][0])
    return do_rpt_inner

def make_report_school(league, school):
    return do_report(get_table_info(league))([school, league])

def xtract_numb(cmb_val):
    return 500 - int(cmb_val.split("^")[0])

def add_sc_rec(accum, new_rec):
    return {"Number": accum["Number"] + [xtract_numb(new_rec)],
            "College": accum["College"] + [new_rec.split("^")[-1]]}

def make_report_dist(league):
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
