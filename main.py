#!/usr/bin/env python3

from configparser import RawConfigParser
from argparse import ArgumentParser
from ff_espn_api import League
from pandas import DataFrame
from operator import add
from functools import reduce
from adjustText import adjust_text

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
plt.style.use("fivethirtyeight")


def get_name(team):
    if team.team_abbrev == 'DAVE':
        return team.team_abbrev
    return "".join([word[0] for word in team.owner.split()])

def expected_wins_by_team(league):
    teams = league.teams
    df = DataFrame(columns=["Points", "Win", "Week", "Team"])
    for team in teams:
        games = [[data[0], data[1], week, get_name(team)] for week,data in enumerate(zip(team.scores,team.won_games))]
        teamDF = DataFrame(games, columns=["Points", "Win", "Week", "Team"])
        # teamDF['Win'] = df['Win'].astype(int)

        # assume that a 0.0 as a score implies that the game hasn't happened
        teamDF = teamDF.loc[teamDF["Points"] > 0]
        df = df.append(teamDF)
    df = df.reset_index(drop=True)

    exp_wins = df.groupby(by="Week")["Points"]\
                 .rank(ascending=True)
                 # .rename(columns={"Points":"Place"})

    df = df.join(exp_wins, lsuffix="orig",rsuffix="ew")
    df.rename(columns={"Pointsew":"Rank", "Pointsorig":"Points"}, inplace=True)
    df["Exp Win"] = df["Rank"] / (len(league.teams) - 1)
    df["Win"] = df["Win"].astype(int)

    df = df.filter(["Team","Exp Win","Win"])\
           .groupby(by="Team")\
           .agg({"Exp Win": "sum", "Win": "sum"})
    return df


def expected_wins(league, weeks):
    allWeeks = DataFrame(columns=["Team","Win","Exp Win"])
    for week in weeks:
        print("getting scores for %d" %(week))
        scores = league.box_scores(week)
        data = []
        for m in scores:
            if m.home_team:
                data.append([week,
                             get_name(m.home_team),
                             m.home_score,
                             m.home_score > m.away_score])
            if m.away_team:
                data.append([week,
                             get_name(m.away_team),
                             m.away_score,
                             m.away_score > m.home_score])

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
    ewins_df = expected_wins_by_team(league)
    draw_agg_dataframe(ewins_df)


if __name__ == "__main__":
    main()
