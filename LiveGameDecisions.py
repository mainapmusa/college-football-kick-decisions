from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from KickDecision import GetFieldGoalDecision
import json
import os
import time
import argparse
import sys
import subprocess
import datetime
import SendTweet

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

def GetMathPrintString(fgVal,goVal,conversionPercent,expectedFromConv,fgPercent):
    message = ""
    message += "Chance to convert on 4th: " + str(conversionPercent) + "\n"
    message += "Expected pts if get 1st: " + str(expectedFromConv) + "\n"
    message += "Value of going for it: " + str(goVal) + "\n"
    message += "Likelihood make FG: " + str(fgPercent) + "\n"
    message += "FG attempt value: " + str(fgVal) + "\n"

    return message


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

def GetKickDecision(gameId, year, week, situationInfo, tweet = False):
    #dec = os.system("python KickDecision.py -GetFieldGoalDecision -tweet -Situation " + " ".join(situationInfo) + " -tweet")
    #dec = os.popen("python KickDecision.py -GetFieldGoalDecision -tweet -Situation " + " ".join(situationInfo)).read()
    liveFileName = "./live_game_logs/"+str(year)+"_"+"week_"+str(week)+".json"
    lifeAlreadyTweetedFileName = "./live_game_logs/"+str(year)+"_"+"week_"+str(week)+"_already_tweeted.json"
    if os.path.isfile(lifeAlreadyTweetedFileName):
        with open(lifeAlreadyTweetedFileName) as data_file:
            alreadyTweeted = json.load(data_file)
    else:
        alreadyTweeted = {}

    print(alreadyTweeted)
    currQtr = situationInfo[0]
    if gameId not in alreadyTweeted:
        alreadyTweeted[gameId] = ""
        print("new game id: " + str(gameId))
    if currQtr in alreadyTweeted[gameId]:
        print(currQtr+" already in game id: "+ gameId)
        return
    print("Qtr "+currQtr+" NOT already in game id: "+ gameId)
    print(alreadyTweeted)

    if os.path.isfile(liveFileName):
        with open(liveFileName) as data_file:
            liveDecisions = json.load(data_file)
    else:
        liveDecisions = {}

    if gameId not in liveDecisions:
        liveDecisions[gameId] = []

    if " ".join(situationInfo) in liveDecisions[gameId]:
        return
    else:
        liveDecisions[gameId].append(" ".join(situationInfo))


    dec = subprocess.check_output("python KickDecision.py -GetFieldGoalDecision -tweet -Situation " + " ".join(situationInfo), shell=True)
    #3 200 20 100 20 21 3 1 10 1

    #dec = subprocess.check_output([sys.executable, "KickDecision.py", "-GetFieldGoalDecision", "-Situation", situationInfo])

    #fgSituation = situationInfo[:3]
    #g4Situation = [situationInfo[3]] + [situationInfo[0]] + situationInfo[4:7] + [situationInfo[2]] + situationInfo[7:]
    #print(fgSituation)
    #print(g4Situation)
    #dec = GetFieldGoalDecision(fgSituation, g4Situation, tweet)
    print(dec)
    fgVal = str(dec).split("Field Goal Expected Value: ")[1][:4]
    goVal = float(str(dec).split("Expected Value Of Going For It: ")[1][:4])
    conversionPercent = str(dec).split("4th Down Conversion Likelihood: ")[1][:4]
    expectedFromConv = str(dec).split("Expected Points For Starting From Converstion Spot: ")[1][:4]


    if fgVal[3] not in "1234567890.":
        fgVal = fgVal[:3]
    if expectedFromConv[3] not in "1234567890.":
        expectedFromConv = expectedFromConv[:3]
    if expectedFromConv[2] not in "1234567890.":
        expectedFromConv = expectedFromConv[:2]
    if expectedFromConv[1] not in "1234567890.":
        expectedFromConv = expectedFromConv[:1]
    fgVal = float(fgVal)
    expectedFromConv = float(expectedFromConv)
    conversionPercent = float(conversionPercent)

    difference = abs(fgVal - goVal)
    if difference < 0.75:
        print("difference is only " + str(difference))
        return
    dist = float(situationInfo[6])
    print("distance: "+dist)
    if dist > 10:
        print("distance is over 10 yards")
        return

    alreadyTweeted[gameId] += currQtr
    print(alreadyTweeted)
    with open(lifeAlreadyTweetedFileName, "w") as file:
        json.dump(alreadyTweeted, file, sort_keys=True, indent=4)

    shouldHaveKicked = True if "GO FOR IT!" not in str(dec) else False
    with open(liveFileName, "w") as file:
        json.dump(liveDecisions, file, sort_keys=True, indent=4)
    print(fgVal)
    print(goVal)
    print(conversionPercent)
    print(expectedFromConv)
    return (fgVal,goVal,conversionPercent,expectedFromConv,shouldHaveKicked)

def InvestigateGame(gameId, homeTeamId, awayTeamId, year, week, tweet = False):
    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")
    browser = webdriver.Chrome(executable_path="/Applications/chromedriver", chrome_options=option)


    #travel to play by play site for each game found for the week
    browser.get("http://www.espn.com/college-football/playbyplay?gameId="+gameId)

    awayWins,awayLosses = map(int,browser.find_element_by_css_selector("div.team.away .record").text.split(",")[0].split("-"))
    homeWins,homeLosses = map(int,browser.find_element_by_css_selector("div.team.home .record").text.split(",")[0].split("-"))

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
    #
    #
    # reverse drives since they are most recent at the top for live games
    #
    #
    drives.reverse()
    for drive in drives:
        try:
            try:
                drive.find_element_by_css_selector(".accordion-header .webview-internal.collapsed").click()
            except:
                pass
            #drive.find_element_by_css_selector(".accordion-header .webview-internal .right .home .team-name").click()
            homeTeam = drive.find_element_by_css_selector(".accordion-header .webview-internal .right .home .team-name").get_attribute("innerHTML")
            awayTeam = drive.find_element_by_css_selector(".accordion-header .webview-internal .right .away .team-name").get_attribute("innerHTML")
            homeScore = drive.find_element_by_css_selector(".accordion-header .webview-internal .right .home .team-score").get_attribute("innerHTML")
            awayScore = drive.find_element_by_css_selector(".accordion-header .webview-internal .right .away .team-score").get_attribute("innerHTML")

            #
            #
            #different location for image url to get offense id
            #
            #
            src = drive.find_element_by_css_selector(".accordion-header .webview-internal .left .team-logo .imageLoaded").get_attribute("src")

            driveNumber += 1
            #print(str(homeTeam)+ " " + str(homeScore))
            #print(str(awayTeam) + " " + str(awayScore))
            #
            #
            #different url
            #
            #
            offenseId = src.replace("http://a1.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/","").split(".")[0]
            #print("offense id: " + str(offenseId))

            #this seems backwards but it works so I'll roll with it
            offenseShortCode = awayTeam if offenseId == homeTeamId else homeTeam
            print("drive number: "+str(driveNumber)+  ",offense team: "+offenseShortCode)

            #get Plays
            plays = drive.find_elements_by_css_selector(".drive-list li")
            #
            #
            # reverse plays since they are most recent at the top for live games
            #
            #
            plays.reverse()
            for play in plays:
                try:
                    attempt = play.find_element_by_css_selector(".post-play").get_attribute("innerHTML").strip()
                    playNumber += 1
                    try:
                        position = play.find_element_by_css_selector("h3").get_attribute("innerHTML").strip()
                        #this also seems backwards, check why
                        if(offenseId == homeTeamId):
                            offensePoints = awayPoints
                            defensePoints = homePoints
                        else:
                            offensePoints = homePoints
                            defensePoints = awayPoints
                        #print("offense points: " + str(offensePoints))
                        #print("defense points: " + str(defensePoints))
                        #if facing a 4th down from inside the opponents 35
                        if IsGameInDoubt4thDown(position, offenseShortCode, qtr, time, offensePoints, defensePoints):
                            #print("\t"+position)
                            #print("\t"+attempt)
                            ballPosition = position[-2:]
                            #print("ball position: "+ str(ballPosition))
                            distance = GetDistanceToGo(position, ballPosition)
                            #print ("offense id: " + str(offenseId))
                            #print ("homeTeamId: " + str(homeTeamId))
                            #print ("home points: " + homePoints)
                            #print ("away points: " + awayPoints)



                            #print("\t\t"+"offense points: " + str(offensePoints) + ",defense points: " + str(defensePoints) + ", position: " + str(ballPosition) + ", drive number: " + str(driveNumber) + ", play number: " + str(playNumber))
                            #print("\t\t"+"quarter: "+ qtr + ", time: "+str(time) +", distance: " + distance)

                            decisionValues = GetKickDecision(gameId, year, week, [str(qtr), str(time), str(ballPosition), str(playNumber), str(offensePoints), str(defensePoints), str(distance), "1", str(driveNumber), "1"], tweet)
                            fgValue = decisionValues[0]
                            go4thValue = decisionValues[1]
                            convPerc = decisionValues[2]
                            expPtsFromConv = decisionValues[3]
                            fgPercent = float(fgValue)/3.0
                            #turn this into a function WasFieldGoalKicked(attempt)
                            kickedFG = True if WasFieldGoalKicked(attempt) else False
                            #print(attempt)
                            #print("kickedFG: " + str(kickedFG))
                            #print("offenseId: " + str(offenseId))
                            #print(go4thValue)
                            #print(decisionValues)
                            #homeResults = {"CorrectKick":0,"CorrectGoForIt":0,"IncorrectKick":0,"IncorrectGoForIt":0,"PlusMinus":0}
                            #awayResults = {"CorrectKick":0,"CorrectGoForIt":0,"IncorrectKick":0,"IncorrectGoForIt":0,"PlusMinus":0}
                            with open("./data/espn_ids.json") as data_file:
                                espnInfo = json.load(data_file)
                            print("about to set up tweet")
                            handles = espnInfo[offenseId]["TwitterHandles"]
                            hashtagName = "#"+espnInfo[offenseId]["Name"].replace(" ","")
                            hashtags = espnInfo[offenseId]["Hashtags"]
                            alwaysHashtags = "#ArtificialIntelligence #MachineLearning"
                            mathMsg = GetMathPrintString(fgValue,go4thValue,convPerc,expPtsFromConv,fgPercent)
                            fullMsg = ""
                            if kickedFG:
                                if fgValue > go4thValue:
                                    #correctly kicked fg
                                    if(offenseId == homeTeamId):
                                        print("home team kick correct")
                                        fullMsg = hashtagName + " smartly kicked the FG on 4th & "+str(distance)+" at the "+str(ballPosition)+"\n" + mathMsg +"\n"+handles+" "+hashtags+" "+alwaysHashtags
                                    else:
                                        print("away team kick correct")
                                        fullMsg = hashtagName + " smartly kicked the FG on 4th & "+str(distance)+" at the "+str(ballPosition)+"\n" + mathMsg +"\n"+handles+" "+hashtags+" "+alwaysHashtags
                                else:
                                    #incorrectly kicked fg
                                    if(offenseId == homeTeamId):
                                        print("home team kick WRONG")
                                        fullMsg = hashtagName + " should have gone for it on 4th & "+str(distance)+" at the "+str(ballPosition)+"\n" + mathMsg +"\n"+handles+" "+hashtags+" "+alwaysHashtags
                                    else:
                                        print("away team kick WRONG")
                                        fullMsg = hashtagName + " should have gone for it on 4th & "+str(distance)+" at the "+str(ballPosition)+"\n" + mathMsg +"\n"+handles+" "+hashtags+" "+alwaysHashtags
                            else:
                                if go4thValue > fgValue:
                                    #correctly went on 4th
                                    if(offenseId == homeTeamId):
                                        print("home team go for it correct")
                                        fullMsg = hashtagName + " smartly went for it on 4th & "+str(distance)+" at the "+str(ballPosition)+"\n" + mathMsg +"\n"+handles+" "+hashtags+" "+alwaysHashtags
                                    else:
                                        print("away team go for it correct")
                                        fullMsg = hashtagName + " smartly went for it on 4th & "+str(distance)+" at the "+str(ballPosition)+"\n" + mathMsg +"\n"+handles+" "+hashtags+" "+alwaysHashtags
                                else:
                                    #incorrectly went on 4th
                                    if(offenseId == homeTeamId):
                                        print("home team go for it WRONG")
                                        fullMsg = hashtagName + " should have kicked on 4th & "+str(distance)+" at the "+str(ballPosition)+"\n" + mathMsg +"\n"+handles+" "+hashtags+" "+alwaysHashtags
                                    else:
                                        print("away team go for it WRONG")
                                        fullMsg = hashtagName + " should have kicked on 4th & "+str(distance)+" at the "+str(ballPosition)+"\n" + mathMsg +"\n"+handles+" "+hashtags+" "+alwaysHashtags
                            print(fullMsg)
                            SendTweet.tweet(fullMsg)
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


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-tweet", "- pass this to tweet at your homies", action='store_true', default=False)

    args = parser.parse_args()
    #print(args)

    tweet = args.tweet

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")

    currentDate = datetime.datetime.now()
    year = currentDate.year
    month = currentDate.month
    day = currentDate.day
    week = datetime.date(year, month, day).isocalendar()[1] - 34
    print(year)
    print(month)
    print(day)
    print(week)

    year = str(year)
    week = str(week)

    print("starting year: "+year)
    yearFileName = "./live_results_logs/"+year+".json"
    #print(yearDecisions)

    while True:
        browser = webdriver.Chrome(executable_path="/Applications/chromedriver", chrome_options=option)

        #TODO: get current years json from file
        if os.path.isfile(yearFileName):
            with open(yearFileName) as data_file:
                yearDecisions = json.load(data_file)
        else:
            yearDecisions = {}

        #navigate to list of games that week
        browser.get("http://www.espn.com/college-football/scoreboard/_/group/80/year/"+year+"/seasontype/2/week/"+week)

        #grab each LIVE game for that week
        #
        #
        # IMPORTANT: THIS GRABS JUST LIVE GAMES
        #
        #
        games = browser.find_elements_by_css_selector(".scoreboard.football.live")

        #get important IDs for each game
        gameAndTeamIds = []
        for game in games:
            gameId = game.get_attribute("id")
            homeTeamId = game.get_attribute("data-homeid")
            awayTeamId = game.get_attribute("data-awayid")
            #if teams is None or if home team or away team in teams
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

            InvestigateGame(game[0], game[1], game[2], year, week, tweet)

        #print(yearDecisions)
        #TODO: write years decision logs back to file

        with open(yearFileName, "w") as file:
            json.dump(yearDecisions, file, sort_keys=True, indent=4)

        print(len(gameAndTeamIds))
        time.sleep(len(gameAndTeamIds)*10)


if __name__ == "__main__":
    main()
