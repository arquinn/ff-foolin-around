#!/usr/bin/env python3

'''
Foolin' around with just how bad yer lineup was
'''

from configparser import RawConfigParser
from argparse import ArgumentParser
from ff_espn_api import League

def get_missed_opportunities(lineup):
    bench = {}
    for player in lineup:
        if player.slot_position == "BE":
            for pos in player.eligible_slots:
                if pos not in bench or bench[pos].points < player.points:
                    bench[pos] = player

    total = 0.0
    for player in lineup:
        if player.slot_position != "BE" and\
           player.slot_position in bench and\
           bench[player.slot_position].points > player.points:
            total += bench[player.slot_position].points - player.points
            print ("shoulda played %s over %s" %(bench[player.slot_position], player))


    return total
def bad_lineup(league, weeks):
    '''Get information about how bad you set your lineup'''
    for week in weeks:
        scores = league.box_scores(week)
        for s in scores:
            get_missed_opportunities(s.home_lineup)




def main():
    '''The main function'''

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
        bad_lineup(league, [1])
    else:
        bad_lineup(league, [1])



if __name__ == "__main__":
    main()
