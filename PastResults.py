from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from KickDecision import GetFieldGoalDecision
import json
import os
import argparse
import sys
import subprocess

#os.system("python KickDecision.py -GetFieldGoalDecision -GraphCompareConferencePointsPerPossession -tweet -Situation 3 200 20 100 20 21 3 1 10 1 -Teams 'Notre Dame' Michigan -Conferences 'Atlantic Coast Conference' 'Southeastern Conference' 'Big 12 Conference'")

def GetDistanceToGo(position, ballPosition):
    distance = position.split("at")[0].split("&amp;")[1].strip()
    if distance == 'Goal':
        distance = ballPosition
    if distance == '0':
        print("DISTANCE GIVEN AS 0 ON ESPN")
        print(position)
        distance = ballPosition
    return distance

def WasFieldGoalKicked(attempt):
    if ("Field Goal" in attempt) or ("FG MISSED" in attempt) or ("FG GOOD" in attempt) or ("FG BLOCKED" in attempt):
        return True
    else:
        return False

def IsGameInDoubt4thDown(position, offenseShortCode, qtr, time, offensePoints, defensePoints):
    #print("\nposition: " + position)
    #print("last 2 spots: '"+position[-2:]+"'")
    #print("offenseShortCode: " + offenseShortCode)
    #print("qtr: " + qtr)
    #print("time: " + str(time))
    #print("defensePoints: " + str(defensePoints))
    #print("offensePoints: " + str(offensePoints))
    # if a 4th down inside the other teams 35
    if (position[0] == '4') and (offenseShortCode not in position) and (int(position[-2:]) <= 35):
        #print("4th down inside the other teams 35")
        # if in the first half and a 3 score game
        if qtr == "1" and (abs(int(offensePoints) - int(defensePoints)) <= 21):
            #print("first qtr and a 3 score game")
            return True
        elif qtr == "2" and (time > 60)  and (abs(int(offensePoints) - int(defensePoints)) <= 21):
            #print("second qtr and a 3 score game and time left in half to score")
            return True
        # if in the 3rd qtr and a 2 score game
        elif qtr == "3" and (abs(int(offensePoints) - int(defensePoints)) <= 14):
            #print("3rd qtr and a 2 score game")
            return True
        # if early in the 4th qtr and a 1 score game
        elif qtr == "4" and (time > 480) and (abs(int(offensePoints) - int(defensePoints)) <= 7):
            #print("early in the 4th qtr and a 1 score game")
            return True

    #print("NOT A CLOSE GAME OR TOO LATE IN THE GAME")
    return False

def GetKickDecision(situationInfo, tweet = False):
    #dec = os.system("python KickDecision.py -GetFieldGoalDecision -tweet -Situation " + " ".join(situationInfo) + " -tweet")
    #dec = os.popen("python KickDecision.py -GetFieldGoalDecision -tweet -Situation " + " ".join(situationInfo)).read()
    dec = subprocess.check_output("python KickDecision.py -GetFieldGoalDecision -tweet -Situation " + " ".join(situationInfo), shell=True)
    #3 200 20 100 20 21 3 1 10 1

    #dec = subprocess.check_output([sys.executable, "KickDecision.py", "-GetFieldGoalDecision", "-Situation", situationInfo])

    #fgSituation = situationInfo[:3]
    #g4Situation = [situationInfo[3]] + [situationInfo[0]] + situationInfo[4:7] + [situationInfo[2]] + situationInfo[7:]
    #print(fgSituation)
    #print(g4Situation)
    #dec = GetFieldGoalDecision(fgSituation, g4Situation, tweet)
    fgVal = str(dec).split("Field Goal Expected Value: ")[1][:4]
    goVal = float(str(dec).split("Expected Value Of Going For It: ")[1][:4])
    if fgVal[3] not in "1234567890":
        fgVal = fgVal[:3]
    fgVal = float(fgVal)
    shouldHaveKicked = True if "GO FOR IT!" not in str(dec) else False
    return (fgVal,goVal,shouldHaveKicked)

def InvestigateGame(gameId, homeTeamId, awayTeamId, tweet = False):
    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")
    browser = webdriver.Chrome(executable_path="/Applications/chromedriver", chrome_options=option)

    homeResults = {"CorrectKick":0,"CorrectGoForIt":0,"IncorrectKick":0,"IncorrectGoForIt":0,"PlusMinus":0}
    awayResults = {"CorrectKick":0,"CorrectGoForIt":0,"IncorrectKick":0,"IncorrectGoForIt":0,"PlusMinus":0}

    #travel to play by play site for each game found for the week
    browser.get("http://www.espn.com/college-football/playbyplay?gameId="+gameId)

    awayWins,awayLosses = map(int,browser.find_element_by_css_selector("div.team.away .record").text.split(",")[0].split("-"))
    homeWins,homeLosses = map(int,browser.find_element_by_css_selector("div.team.home .record").text.split(",")[0].split("-"))
    homeWin = "home-winner" in browser.find_element_by_css_selector(".game-strip.game-package.college-football.post").get_attribute("class");


    if homeWin:
        homeWins -= 1
        awayLosses -= 1
    else:
        homeLosses -= 1
        awayWins -= 1

    homeWinPercent = homeWins/(homeWins+homeLosses) if (homeWins+homeLosses) > 0 else 0.5
    awayWinPercent = awayWins/(awayWins+awayLosses) if (awayWins+awayLosses) > 0 else 0.5
    #print("homeWins: " + str(homeWins) + ", homeLosses: " + str(homeLosses) + ", win %: " + str(homeWinPercent))
    #print("awayWins: " + str(awayWins) + ", awayLosses: " + str(awayLosses) + ", win %: " + str(awayWinPercent))


    #return

    #get list of drives
    drives = browser.find_elements_by_css_selector("#gamepackage-drives-wrap li.accordion-item")

    #set the initial offense and defense points, at end of each drive reset these
    homePoints = 0
    awayPoints = 0
    offensePoints = 0
    defensePoints = 0
    driveNumber = 0
    playNumber = 0
    #drill into each drive of that list of drives for this game
    for drive in drives:
        try:
            homeTeam = drive.find_element_by_css_selector(".accordion-header .webview-internal .right .home .team-name").get_attribute("innerHTML")
            awayTeam = drive.find_element_by_css_selector(".accordion-header .webview-internal .right .away .team-name").get_attribute("innerHTML")
            homeScore = drive.find_element_by_css_selector(".accordion-header .webview-internal .right .home .team-score").get_attribute("innerHTML")
            awayScore = drive.find_element_by_css_selector(".accordion-header .webview-internal .right .away .team-score").get_attribute("innerHTML")
            src = drive.find_element_by_css_selector(".accordion-header .webview-internal .left .team-logo").get_attribute("src")

            driveNumber += 1
            #print(str(homeTeam)+ " " + str(homeScore))
            #print(str(awayTeam) + " " + str(awayScore))
            offenseId = src.replace("http://a.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/","").split(".")[0]
            #print("offenseId: " + str(offenseId))

            #this seems backwards but it works so I'll roll with it
            offenseShortCode = awayTeam if offenseId == homeTeamId else homeTeam
            print("drive number: "+str(driveNumber)+  ",offense team: "+offenseShortCode)

            #get Plays
            plays = drive.find_elements_by_css_selector(".drive-list li")
            for play in plays:
                try:
                    attempt = play.find_element_by_css_selector(".post-play").get_attribute("innerHTML").strip()
                    playNumber += 1

                    #print(time)
                    #print(qtr)
                    try:
                        position = play.find_element_by_css_selector("h3").get_attribute("innerHTML").strip()
                        #this also seems backwards, check why
                        if(offenseId == homeTeamId):
                            offensePoints = awayPoints
                            defensePoints = homePoints
                        else:
                            offensePoints = homePoints
                            defensePoints = awayPoints
                        #if facing a 4th down from inside the opponents 35
                        if IsGameInDoubt4thDown(position, offenseShortCode, qtr, time, offensePoints, defensePoints):
                            #print("\t"+position)
                            #print("\t"+attempt)
                            ballPosition = position[-2:]
                            distance = GetDistanceToGo(position, ballPosition)
                            #print ("offense id: " + str(offenseId))
                            #print ("homeTeamId: " + str(homeTeamId))
                            #print ("home points: " + homePoints)
                            #print ("away points: " + awayPoints)



                            #print("\t\t"+"offense points: " + str(offensePoints) + ",defense points: " + str(defensePoints) + ", position: " + str(ballPosition) + ", drive number: " + str(driveNumber) + ", play number: " + str(playNumber))
                            #print("\t\t"+"quarter: "+ qtr + ", time: "+str(time) +", distance: " + distance)

                            decisionValues = GetKickDecision([str(qtr), str(time), str(ballPosition), str(playNumber), str(offensePoints), str(defensePoints), str(distance), "1", str(driveNumber), "1"], tweet)
                            fgValue = decisionValues[0]
                            go4thValue = decisionValues[1]
                            #turn this into a function WasFieldGoalKicked(attempt)
                            kickedFG = True if WasFieldGoalKicked(attempt) else False
                            #print(attempt)
                            #print("kickedFG: " + str(kickedFG))
                            #print("offenseId: " + str(offenseId))
                            #print(go4thValue)
                            #print(decisionValues)
                            #homeResults = {"CorrectKick":0,"CorrectGoForIt":0,"IncorrectKick":0,"IncorrectGoForIt":0,"PlusMinus":0}
                            #awayResults = {"CorrectKick":0,"CorrectGoForIt":0,"IncorrectKick":0,"IncorrectGoForIt":0,"PlusMinus":0}
                            if kickedFG:
                                if fgValue > go4thValue:
                                    #correctly kicked fg
                                    if(offenseId == homeTeamId):
                                        homeResults["CorrectKick"] +=1
                                        homeResults["PlusMinus"] += (fgValue-go4thValue)
                                        print("home team kick correct")
                                    else:
                                        awayResults["CorrectKick"] +=1
                                        awayResults["PlusMinus"] += (fgValue-go4thValue)
                                        print("away team kick correct")
                                else:
                                    #incorrectly kicked fg
                                    if(offenseId == homeTeamId):
                                        homeResults["IncorrectKick"] +=1
                                        homeResults["PlusMinus"] += (fgValue-go4thValue)
                                        print("home team kick WRONG")
                                    else:
                                        awayResults["IncorrectKick"] +=1
                                        awayResults["PlusMinus"] += (fgValue-go4thValue)
                                        print("away team kick WRONG")
                            else:
                                if go4thValue > fgValue:
                                    #correctly went on 4th
                                    if(offenseId == homeTeamId):
                                        homeResults["CorrectGoForIt"] +=1
                                        homeResults["PlusMinus"] += (go4thValue-fgValue)
                                        print("home team go for it correct")
                                    else:
                                        awayResults["CorrectGoForIt"] +=1
                                        awayResults["PlusMinus"] += (go4thValue-fgValue)
                                        print("away team go for it correct")
                                else:
                                    #incorrectly went on 4th
                                    if(offenseId == homeTeamId):
                                        homeResults["IncorrectGoForIt"] +=1
                                        homeResults["PlusMinus"] += (go4thValue-fgValue)
                                        print("home team go for it WRONG")
                                    else:
                                        awayResults["IncorrectGoForIt"] +=1
                                        awayResults["PlusMinus"] += (go4thValue-fgValue)
                                        print("away team go for it WRONG")

                    except:
                        pass

                    if "End" not in attempt:
                        stuff = attempt.split(")")[0].split("-")
                        time = stuff[0].strip().replace("(","")
                        time = int(time.split(":")[0])*60 + int(time.split(":")[1])
                        qtr = stuff[1].strip()[0]
                    else:
                        #get quarter number and say play started with 60*15 seconds left
                        qtr = str(int(qtr)+1)
                        time = 15*60

                except:
                    pass

            #go through each play

            #set end of drive score for next drive to start with
            homePoints = homeScore
            awayPoints = awayScore
        except:
            pass

    browser.quit()
    return (homeResults,awayResults)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-years", "- what year to check yo", nargs='+', type=int)
    parser.add_argument("-weeks", "- list of weeks to check (could be single week obvs)", nargs='+', type=int)
    parser.add_argument("-teams", "- list of teams to check (could be single team obvs)", nargs='+', type=int)
    parser.add_argument("-tweet", "- pass this to tweet at your homies", action='store_true', default=False)

    args = parser.parse_args()
    #print(args)

    years = list(map(str, args.years))
    weeks = list(map(str, args.weeks))
    if args.teams is not None:
        teams = list(map(str, args.teams))
    else:
        teams = []
    print(teams)
    tweet = args.tweet

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")




    for year in years:
        print("starting year: "+year)
        yearFileName = "./past_results_logs/"+year+".json"
        #print(yearDecisions)

        for week in weeks:
            browser = webdriver.Chrome(executable_path="/Applications/chromedriver", chrome_options=option)
            print("starting week: " + week)
            #TODO: get current years json from file
            if os.path.isfile(yearFileName):
                with open(yearFileName) as data_file:
                    yearDecisions = json.load(data_file)
            else:
                yearDecisions = {}

            #navigate to list of games that week
            browser.get("http://www.espn.com/college-football/scoreboard/_/group/80/year/"+year+"/seasontype/2/week/"+week)

            #grab each game for that week
            games = browser.find_elements_by_css_selector(".scoreboard.football")

            #get important IDs for each game
            gameAndTeamIds = []
            for game in games:
                gameId = game.get_attribute("id")
                homeTeamId = game.get_attribute("data-homeid")
                awayTeamId = game.get_attribute("data-awayid")
                #if teams is None or if home team or away team in teams
                if (len(teams) == 0) or (homeTeamId in teams) or (awayTeamId in teams):
                    gameAndTeamIds.append([gameId,homeTeamId,awayTeamId])

            print(gameAndTeamIds)
            browser.quit()
            #drill into each game for the week that we found
            for game in gameAndTeamIds:

                #TODO: get this id from already loaded dictionary, create week if it doesn't exist
                #if home team does not exist in this years dict, add it
                if game[1] not in yearDecisions:
                    yearDecisions[game[1]] = {}
                #if away team does not exist in this years dict, add it
                if game[2] not in yearDecisions:
                    yearDecisions[game[2]] = {}

                yearDecisions[game[1]][week],yearDecisions[game[2]][week] = InvestigateGame(game[0], game[1], game[2], tweet)

            #print(yearDecisions)
            #TODO: write years decision logs back to file

            with open(yearFileName, "w") as file:
                json.dump(yearDecisions, file, sort_keys=True, indent=4)



if __name__ == "__main__":
    main()
