#!/usr/bin/env python3

from configparser import RawConfigParser
from argparse import ArgumentParser
from ff_espn_api import League
from pandas import DataFrame
from adjustText import adjust_text

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
plt.style.use("fivethirtyeight")

from expected_wins import *


def draw_agg_dataframe(df):
    agg = df.groupby("Team")\
            .agg({"Win":"sum","Exp Win":"sum"})\
            .rename(columns = {"Win":"Wins", "Exp Win": "Exp Wins"})\
            .sort_values(by="Exp Wins")

    ax = agg.plot(kind="scatter", x="Exp Wins", y="Wins", title="Exp Wins vs. Wins")

    ann = []
    for x,y,val in zip(agg['Exp Wins'], agg['Wins'], agg.index.to_series()):
        ann.append(ax.text(x,y,val))

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

    week = args.week
    if week == 0:
        week = league.nfl_week

    print("On week %d" %(league.current_week))
    ewins_df = expected_wins(league)
    draw_agg_dataframe(ewins_df)


if __name__ == "__main__":
    main()
