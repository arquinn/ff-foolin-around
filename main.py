#!/usr/bin/env python

from configparser import RawConfigParser
from argparse import ArgumentParser
from ff_espn_api import League





def main():
    parser = ArgumentParser(description="Script to look at ff data")
    parser.add_argument("year", metavar="YEAR", type=int,
                        help="the year to check out (default to 2019)",
                        nargs='?',default=2019)

    args = parser.parse_args()

    config = RawConfigParser()
    config.read("fantasy.config")

    league = League(config['LEAGUE_INFO']["LEAGUE_ID"],\
                    args.year,\
                    config['LEAGUE_INFO']['s2'],\
                    config['LEAGUE_INFO']['SWID'])


    #print(league_data(league))




if __name__ == "__main__":
    main()
