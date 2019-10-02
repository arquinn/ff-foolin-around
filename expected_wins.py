#!/usr/bin/env python3

from ff_espn_api import League
from pandas import DataFrame

def get_name(team):
    if team.team_abbrev == 'DAVE':
        return team.team_abbrev
    return "".join([word[0] for word in team.owner.split()])


def expected_wins(league):
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
