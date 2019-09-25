#!/usr/bin/env python

from configparser import RawConfigParser
from argparse import ArgumentParser
from ff_espn_api import League
from pandas import DataFrame
from operator import add
from functools import reduce
from adjustText import adjust_text
from fontTools.ttLib import TTFont

import pandas as pd
import matplotlib
matplotlib.use('module://mplcairo.qt')

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
plt.style.use("fivethirtyeight")

eprop = (fm.FontProperties(fname="NotoColorEmoji.ttf"), "NotoColorEmoji.ttf")

tmp = matplotlib.font_manager.FontProperties(family=plt.rcParams["font.family"])
dprop = (tmp, matplotlib.font_manager.findfont(tmp))

def checkForChar(string):
    # Hacky McHackerson:
    if all(ord(c) < 128 for c in string):
        return dprop[0]
    return eprop[0]


def get_name(team):
    if team.team_abbrev == 'DAVE':
        return team.team_abbrev
    return "".join([word[0] for word in team.owner.split()])

def expected_wins(league, weeks):
    allWeeks = DataFrame(columns=["Team","Win","Exp Win"])
    for week in weeks:
        scores = league.box_scores(week)
        data = reduce(add,
                      [[[week, get_name(m.home_team),
                         m.home_score, m.home_score > m.away_score],\
                        [week, get_name(m.away_team),
                         m.away_score, m.away_score > m.home_score]]
                       for m in scores])
        df = DataFrame(data, columns=["Week","Team", "Points", "Win"])
        df = df.sort_values(by="Points")\
               .reset_index(drop=True)\
               .filter(["Team","Win"])
        df['Win'] = df['Win'].astype(int)
        df["Exp Win"] = (df.index + 0.0)  / (len(df.index) - 1)

        allWeeks = allWeeks.append(df)

    print (allWeeks)
    return allWeeks

def draw_agg_dataframe(df):
    agg = df.groupby("Team")\
            .agg({"Win":"sum","Exp Win":"sum"})\
            .rename(columns = {"Win":"Wins", "Exp Win": "Exp Wins"})\
            .sort_values(by="Exp Wins")

    ax = agg.plot(kind="scatter", x="Exp Wins", y="Wins", title="Exp Wins vs. Wins")

    ann = []
    for x,y,val in zip(agg['Exp Wins'], agg['Wins'], agg.index.to_series()):
        p = checkForChar(val)
        ann.append(ax.text(x,y,val, fontproperties=p))

    #identiy line:
    maxW = agg['Wins'].max()
    ident = range(maxW+1)
    maxWs = [maxW for i in ident]

    #ax.plot(ident, ident, color='black)
    ax.fill_between(ident, ident, color='red', alpha=0.3)
    ax.fill_between(ident, ident, maxWs, color='blue', alpha=0.3)

    ax.set_xlim(0, maxW)
    ax.set_ylim(-.25, maxW + .25)
    ax.text(.125, maxW - .25, "Lucky", color='blue')
    ax.text(maxW - .5, .25,"Unlucky", color='red')

    adjust_text(ann, agg['Exp Wins'], agg['Wins'])

    plt.show()

ewins_df = []
def main():
    parser = ArgumentParser(description="Script to look at ff data")
    parser.add_argument("year", metavar="YEAR", type=int,
                        help="the year to check out (default to 2019)",
                        nargs='?',default=2019)
    parser.add_argument("week", metavar="WEEK", type=int,
                        help="How many weeks to check out (defautl to all)",
                        nargs='?',default=0)

    args = parser.parse_args()

    config = RawConfigParser()
    config.read("fantasy.config")

    league = League(config['LEAGUE_INFO']["LEAGUE_ID"],\
                    args.year,\
                    config['LEAGUE_INFO']['s2'],\
                    config['LEAGUE_INFO']['SWID'])


    if args.week == 0:
        ewins_df = expected_wins(league, range(1, league.nfl_week + 1))
    else:
        ewins_df = expected_wins(league, range(1, args.week + 1))
    draw_agg_dataframe(ewins_df)



if __name__ == "__main__":
    main()
