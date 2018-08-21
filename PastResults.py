from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import os
import argparse

#os.system("python KickDecision.py -GetFieldGoalDecision -GraphCompareConferencePointsPerPossession -tweet -Situation 3 200 20 100 20 21 3 1 10 1 -Teams 'Notre Dame' Michigan -Conferences 'Atlantic Coast Conference' 'Southeastern Conference' 'Big 12 Conference'")


'''
NOTES:
Get the Away team ID from the left side of the page header
Get the home team ID from the left side of the page header

Get the ID of the logo from this drive's accordion
  use to know if home or away team
  get the shortened value (STAN vs RICE) from score region on right of accordion

Now know who has the ball and can use that to compare if on own or opponents side of the ball (50 just says 50, neither team)
  if on own side of ball then do not do kick decision
  if beyond 35 do not do kick decision
'''


'''
GetWeeksForYear() -> returns list of weeks to check
for week in weeks:
    Send 'weekly round up for *YEAR* week *WEEK*' tweet
    GetWrongCalls()
        start crawling ESPN
        for each game in this week:
            go to play by play page
            get overall info (home team id, away team id, etc)
            for each drive:
                for each play:
                    if 4th down inside the 35 happened(also maybe if close game and not 4th quarter):
                        get decision and tweet
                        (later find if they chose right decision)

'''

def GetKickDecision(situationInfo, tweet = False):
    print("tweet decision?:  "+ str(tweet))
    print(situationInfo)
    print(" ".join(situationInfo))
    os.system("python KickDecision.py -GetFieldGoalDecision -tweet -Situation " + " ".join(situationInfo) + " -tweet")
    #os.system("python KickDecision.py -GetFieldGoalDecision -tweet -Situation " + " ".join(situationInfo))
    #3 200 20 100 20 21 3 1 10 1

def InvestigateGame(gameId, homeTeamId, awayTeamId, tweet = False):
    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")
    browser = webdriver.Chrome(executable_path="/Applications/chromedriver", chrome_options=option)

    #travel to play by play site for each game found for the week
    browser.get("http://www.espn.com/college-football/playbyplay?gameId="+gameId)

    #get list of drives
    drives = browser.find_elements_by_css_selector("#gamepackage-drives-wrap li.accordion-item")

    #set the initial offense and defense points, at end of each drive reset these
    homePoints = 0
    awayPoints = 0
    offensePoints = 0
    defensePoints = 0
    driveNumber = 0
    PlayNumber = 0
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
            #print(offenseId)
            #print(homeTeamId)

            #this seems backwards but it works so I'll roll with it
            offenseShortCode = awayTeam if offenseId == homeTeamId else homeTeam
            print("drive number: "+str(driveNumber)+  ",offense team: "+offenseShortCode)

            #get Plays
            plays = drive.find_elements_by_css_selector(".drive-list li")
            for play in plays:
                try:
                    attempt = play.find_element_by_css_selector(".post-play").get_attribute("innerHTML").strip()
                    PlayNumber += 1

                    #print(time)
                    #print(qtr)
                    try:
                        position = play.find_element_by_css_selector("h3").get_attribute("innerHTML").strip()
                        #if facing a 4th down from inside the opponents 35
                        if (position[0] == '4') and (offenseShortCode not in position) and (int(position[-2:]) <= 35):
                            print("\t"+position)
                            print("\t"+attempt)
                            ballPosition = position[-2:]
                            distance = position.split("at")[0].split("&amp;")[1].strip()
                            #print ("offense id: " + str(offenseId))
                            #print ("homeTeamId: " + str(homeTeamId))
                            #print ("home points: " + homePoints)
                            #print ("away points: " + awayPoints)

                            #this also seems backwards, check why
                            if(offenseId == homeTeamId):
                                offensePoints = awayPoints
                                defensePoints = homePoints
                            else:
                                offensePoints = homePoints
                                defensePoints = awayPoints

                            print("\t\t"+"offense points: " + str(offensePoints) + ",defense points: " + str(defensePoints) + ", position: " + str(ballPosition) + ", drive number: " + str(driveNumber) + ", play number: " + str(PlayNumber))
                            print("\t\t"+"quarter: "+ qtr + ", time: "+str(time) +", distance: " + distance)

                            GetKickDecision([str(qtr), str(time), str(ballPosition), str(PlayNumber), str(offensePoints), str(defensePoints), str(distance), "1", str(driveNumber), "1"], tweet)

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

    parser.add_argument("-years", "- what year to check yo", nargs='+', type=int)
    parser.add_argument("-weeks", "- list of weeks to check (could be single week obvs)", nargs='+', type=int)
    parser.add_argument("-tweet", "- pass this to tweet at your homies", action='store_true', default=False)

    args = parser.parse_args()
    print args

    years = list(map(str, args.years))
    weeks = list(map(str, args.weeks))
    tweet = args.tweet

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")

    browser = webdriver.Chrome(executable_path="/Applications/chromedriver", chrome_options=option)

    for year in years:
        print("starting year: "+year)
        for week in weeks:
            print("starting week: "+week)

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
                gameAndTeamIds.append([gameId,homeTeamId,awayTeamId])


            print(gameAndTeamIds)
            browser.quit()
            #drill into each game for the week that we found
            for game in gameAndTeamIds:
                InvestigateGame(game[0], game[1], game[2], tweet)



if __name__ == "__main__":
    main()