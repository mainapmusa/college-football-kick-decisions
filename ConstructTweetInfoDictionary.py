from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import os
import argparse


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-years", "- what year to check yo", nargs='+', type=int)
    parser.add_argument("-weeks", "- list of weeks to check (could be single week obvs)", nargs='+', type=int)
    #parser.add_argument("-tweet", "- pass this to tweet at your homies", action='store_true', default=False)

    args = parser.parse_args()
    #print(args)

    years = list(map(str, args.years))
    weeks = list(map(str, args.weeks))
    #tweet = args.tweet

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")

    browser = webdriver.Chrome(executable_path="/Applications/chromedriver", chrome_options=option)



    for year in years:
        print("starting year: "+year)

        #TODO: get current years json from file


        for week in weeks:
            if os.path.isfile("./data/espn_ids.json"):
                with open("./data/espn_ids.json") as data_file:
                    espnIds = json.load(data_file)
            else:
                espnIds = {}
            print("starting week: "+week)

            #navigate to list of games that week
            browser.get("http://www.espn.com/college-football/scoreboard/_/group/80/year/"+year+"/seasontype/2/week/"+week)

            #grab each game for that week
            games = browser.find_elements_by_css_selector(".scoreboard.football")

            for game in games:
                #gameId = game.get_attribute("id")
                homeTeamId = game.get_attribute("data-homeid")
                awayTeamId = game.get_attribute("data-awayid")
                if homeTeamId not in espnIds:
                    homeTeamName = game.find_element_by_css_selector("td.home .sb-team-short").text
                    homeTeamShortCode = game.find_element_by_css_selector("td.home span.sb-team-abbrev").get_attribute("innerHTML")
                    print("homeTeamId: "+homeTeamId)
                    print("homeTeamName: "+homeTeamName)
                    print("homeTeamShortCode: "+homeTeamShortCode)
                    espnIds[homeTeamId] = {"Name":homeTeamName,"ShortCode":homeTeamShortCode}

                if awayTeamId not in espnIds:
                    awayTeamName = game.find_element_by_css_selector("td.away .sb-team-short").text
                    awayTeamShortCode = game.find_element_by_css_selector("td.away span.sb-team-abbrev").get_attribute("innerHTML")
                    print("awayTeamId: "+awayTeamId)
                    print("awayTeamName: "+awayTeamName)
                    print("awayTeamShortCode: "+awayTeamShortCode)
                    espnIds[awayTeamId] = {"Name":awayTeamName,"ShortCode":awayTeamShortCode}


            with open("./data/espn_ids.json", "w") as file:
                 json.dump(espnIds, file, sort_keys=True, indent=4)


            browser.quit()
            #drill into each game for the week that we found

            #print(yearDecisions)
        #TODO: write years decision logs back to file




if __name__ == "__main__":
    main()
