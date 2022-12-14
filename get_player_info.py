#!/usr/bin/python
# Copyright (c) 2022 Warren Usui
# This code is licensed under the MIT license (see LICENSE for details)
"""
Scrape ESPN for college info on NFL and NBA players
"""
import string
import re
import json
from functools import reduce
import requests
from bs4 import BeautifulSoup
import pandas as pd

def read_league_tms(league):
    """ Monad that gets team links """
    return requests.get(f"https://www.espn.com/{league}/teams").text

def read_a_team(suffix):
    """ Monad that gets a specific team roster """
    return requests.get(''.join(["https://www.espn.com", suffix])).text

def get_soup(url_data):
    """ Is it soup yet? """
    return BeautifulSoup(url_data, "html.parser")

def get_roster_list(league):
    """ Extract team links """
    return list(map(lambda a : a.attrs['href'],
                get_soup(read_league_tms(league)).find_all(
                "a", {'href': re.compile(fr'/.*{league}/team/roster/_/.*')})))

def pare_dataf(dframe):
    """ Only extract data that we are interested in """
    return dframe[['Name', 'POS', 'College']]

def clean_jersey_numb(unclean_list):
    """ Remove numbers from player names (artifact of pandas) """
    return list(map(lambda a: [a[0].rstrip(string.digits), a[1], a[2]],
                    unclean_list))

def get_plyr_tbls(team_info):
    """ Isolate individual player records """
    return list(map(lambda a: list(a.iterrows()),
                    list(map(pare_dataf, team_info))))

def reassemble(ptable):
    """ wrapper to convert dataframe to python list """
    return clean_jersey_numb(list(map(lambda a: a[1].to_list(), ptable)))

def get_players_on_team(team_link):
    """ extract list of records for players on a team """
    return list(map(reassemble, get_plyr_tbls(team_link)))

def flatten_a_level(team_lists):
    """ flatten list of lists into one list """
    return reduce(lambda a, b: a + b, team_lists, [])

def get_team_list(team_ind):
    """ get one table of all players (for nfl, offense, defense and
        special teams are separated) """
    return flatten_a_level(get_players_on_team(team_ind))

def get_full_name(team_link):
    """ convert team name in link to properly spaced and capitalized name """
    return string.capwords(team_link.split("/")[-1].replace('-', ' '))

def extract_team(team_link):
    """ Read team information and return that information plus a team name
        suitable for displaying """
    return pd.read_html(read_a_team(team_link)), get_full_name(team_link)

def tm_name_adder(tname):
    """ Take pro team name (in tname) and concatenate that into list of
        information for a player """
    def tna_inner(real_data):
        return real_data + [tname]
    return tna_inner

def add_team_names(extr_data):
    """ Make sure team name is added to all player records """
    return list(map(tm_name_adder(extr_data[1]), get_team_list(extr_data[0])))

def collect_players_for_team(team_link):
    """ get players on a team (complete information in a list) """
    return add_team_names(extract_team(team_link))

def find_all_players(league):
    """ get all players in the league """
    return flatten_a_level(list(map(collect_players_for_team,
                     get_roster_list(league))))

def format_player(player):
    """ Convert player information into a dict """
    return dict(zip(['Name', 'Pos', 'School', 'Team'], player))

def fmt_all_plyrs(league):
    """ Convert all player information into dicts """
    return list(map(format_player, find_all_players(league)))

def write_league(league):
    """ Monad that saves player information for league """
    with open(f"{league}.json", "w", encoding='utf8') as outfile:
        outfile.write(json.dumps(fmt_all_plyrs(league), indent=4,
                                 ensure_ascii=False))

if __name__ == "__main__":
    write_league("nba")
    write_league("nfl")
