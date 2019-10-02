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
    residuals = output[1]
    model = output[0]

    return 1.0 - (residuals[0] / SST), model


def main():
    config = RawConfigParser()
    config.read("fantasy.config")
    dfs = []

    for year in range(2015, 2019):

        league = League(config['LEAGUE_INFO']["LEAGUE_ID"],\
                        year,\
                        config['LEAGUE_INFO']['s2'],\
                        config['LEAGUE_INFO']['SWID'])

        df = expected_wins(league)
        dfs.append(df)

    df = dfs[0]
    for frame in dfs[1:]:
        df = df.append(frame)

    print (regression([df['Exp Win']], df['Win']))
    #ew_v_w(df)


if __name__ == "__main__":
    main()
