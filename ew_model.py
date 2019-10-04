#!/usr/bin/env python3

from configparser import RawConfigParser
from ff_espn_api import League
from expected_wins import *
import numpy as np
from plot import *

def regression(x,y):
    npy = np.array(y)
    npx = np.vstack([x,np.ones(len(x[0]))]).T

    y_bar = sum(npy) / len(npy)
    SST = sum([(float(i) - float(y_bar))**2 for i in npy]) + 0.0

    output = np.linalg.lstsq(npx,npy)

    # apparently... residuals doesn't always exist!? 
    model = output[0]

    residuals = 0.0
    for xvals, yval in zip(npx, npy):
        yest = sum(model * xvals)
        residuals += (yval - yest)**2
        
    return 1.0 - (residuals / SST), model




def main():
    config = RawConfigParser()
    config.read("fantasy.config")
    dfs = []
    dfs_week = []
    dfs_remain = []

    for year in range(2015, 2019):
        league = League(config['LEAGUE_INFO']["LEAGUE_ID"],\
                        year,\
                        config['LEAGUE_INFO']['s2'],\
                        config['LEAGUE_INFO']['SWID'])

        df = expected_wins(league)
        df = opponent_ew(league, df)
        dfs.append(df)

        for eweek in range(1,14):
            dfstart = expected_wins(league, (0, eweek))
            df = opponent_ew(league, dfstart, (0, eweek))

            df_left = opponent_ew(league, dfstart, (eweek, 14))
            
            print (year, eweek)

            if len(dfs_week) >= eweek:
                dfs_week[eweek -1 ] = dfs_week[eweek - 1].append(df)
            else:
                dfs_week.append(df)

            if len(dfs_remain) >= eweek:
                dfs_remain[eweek -1 ] = dfs_remain[eweek - 1].append(df_left)
            else:
                dfs_remain.append(df_left)

    df = dfs[0]
    for frame in dfs[1:]:
        df = df.append(frame)

    print ("full season correlation and model", regression([df['Exp Win']], df['Win']))

    for week, data in enumerate(zip(dfs_week, dfs_remain)):
        df_week = data[0]
        df_remain = data[1]
        

        # df_week is now all data for up to week i 
        df_after = DataFrame()
        df_after['Exp Win'] = df['Exp Win'] - df_week['Exp Win']  
        df_after['Win'] = df['Win'] - df_week['Win']

        print (week, regression([df_week['Exp Win'], df_week['Opp Exp Win'], df_remain['Opp Exp Win']], df_after['Win']))



if __name__ == "__main__":
    main()
