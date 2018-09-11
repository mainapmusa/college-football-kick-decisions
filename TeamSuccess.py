import json
import os
import argparse


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-years", "- what year to check yo", nargs='+', type=int)
    parser.add_argument("-weeks", "- list of weeks to check (could be single week obvs)", nargs='+', type=int)
    parser.add_argument("-teams", "- list of teams to check (could be single team obvs)", nargs='+', type=int)
    parser.add_argument("-tweet", "- pass this to tweet at your homies", action='store_true', default=False)

    args = parser.parse_args()
    #print(args)

    years = list(map(str, args.years))
    #weeks = list(map(str, args.weeks))



    for year in years:
        totals = []
        with open("./past_results_logs/"+year+".json") as data_file:
            yearDecisions = json.load(data_file)
        for team, weeks in yearDecisions.items():
            total = 0
            for v,week in weeks.items():
                total += week["PlusMinus"]
            totals.append((team,total))

    sortedTotals = sorted(totals, key=lambda x: x[1])
    worst = sortedTotals[:5]
    best = reversed(sortedTotals[-5:])
    with open("./data/espn_ids.json") as data_file:
        espnInfo = json.load(data_file)

    print("\n\n Top Worst:")
    for team in worst:
        print(espnInfo[team[0]]["Name"])
        print(team[1])

    print("\n\n Top Best:")
    for team in best:
        print(espnInfo[team[0]]["Name"])
        print(team[1])

if __name__ == "__main__":
    main()
