import json
import os
import argparse
from SendTweet import tweet


def GetTeamsRanking(teams, year, best = True, week = ""):
    if week == "":
        message = "Year: "+year+"\n" + ("Best" if best else "Worst") + " FG decisions\n"
    else:
        message = "Year: "+year+" Week: "+week+"\n" + ("Best" if best else "Worst") + " FG decisions\n"

    message += GetRankingString(teams)
    return message

def GetRankingString(teams):
    with open("./data/espn_ids.json") as data_file:
        espnInfo = json.load(data_file)
    ranking = ""
    spot = 1
    for team in teams:
        ranking += (str(spot)+". "+espnInfo[team[0]]["Name"] + " - " +espnInfo[team[0]]["TwitterHandles"] +"\n")
        ranking += ("\t"+ ("+" if team[1] > 0 else "") +str(team[1])+"\n")
        spot +=1
    return ranking

def GetPlusMinusTotals(year,date=""):
    totals = []
    with open("./past_results_logs/"+year+".json") as data_file:
        yearDecisions = json.load(data_file)
    with open("./data/espn_ids.json") as data_file:
        espnInfo = json.load(data_file)
    for team, weeks in yearDecisions.items():
        total = 0
        for v,week in weeks.items():
            if (date == "") or (v == date):
                total += week["PlusMinus"]
        if team in espnInfo:
            totals.append((team,round(total,2)))

    return sorted(totals, key=lambda x: x[1])

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-years", "- what year to check yo", nargs='+', type=int)
    parser.add_argument("-weeks", "- list of weeks to check (could be single week obvs)", nargs='+', type=int)
    parser.add_argument("-teams", "- list of teams to check (could be single team obvs)", nargs='+', type=int)
    #parser.add_argument("-corr", "- try to find correlation for full year", action='store_true', default=False)


    args = parser.parse_args()
    #print(args)

    topCount = 5
    years = list(map(str, args.years))
    if args.weeks is not None:
        dates = list(map(str, args.weeks))
    else:
        dates = []



    for year in years:
        if len(dates) > 0:
            for date in dates:
                sortedTotals = GetPlusMinusTotals(year,date)

                worst = sortedTotals[:topCount]
                best = reversed(sortedTotals[-topCount:])
                print(GetTeamsRanking(worst,year,False,date))
                print(GetTeamsRanking(best,year,True,date))
        else:
            sortedTotals = GetPlusMinusTotals(year)
            worst = sortedTotals[:topCount]
            best = reversed(sortedTotals[-topCount:])
            print(GetTeamsRanking(worst,year,False))
            print(GetTeamsRanking(best,year,True))

if __name__ == "__main__":
    main()
