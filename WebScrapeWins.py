from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json

def main():
    yearsToUse = ["2005","2006","2007","2008","2009","2010","2011","2012","2013"]
    records = {}

    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")

    browser = webdriver.Chrome(executable_path="/Applications/chromedriver", chrome_options=option)

    browser.get("http://football.stassen.com/cgi-bin/records/show-team.pl")

    delay = 4
    try:
        lastElement = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "http://football.stassen.com/records/compute-request.html")))
        print("found!")
    except TimeoutException:
        print "Loading took too much time!"

    # find_elements_by_xpath returns an array of selenium objects.
    #teams = browser.find_elements_by_partial_link_text("fetch-team")
    teams = browser.find_elements_by_xpath("//td/a[starts-with(@href, '/cgi-bin')]")
    # use list comprehension to get the actual repo titles and not the selenium objects.
    #try:
    for link in teams:
        option = webdriver.ChromeOptions()
        option.add_argument(" - incognito")
        browser = webdriver.Chrome(executable_path="/Applications/chromedriver", chrome_options=option)
        browser.get(link.get_attribute("href"))



        #print(link.get_attribute("href"))
        team = ConvertTeamNames(link.get_attribute("href").split("=")[1].replace("_"," "))


        #browser.get(link.get_attribute("href"))
        #print("Start")
        print(team)
        rows = browser.find_elements_by_xpath("//tr[@align='CENTER']")
        for row in rows:
            try:
                #newbie = row.find_element_by_css_selector("td:first-child a")
                #print(newbie.get_attribute('innerHTML'))
                year = row.find_element_by_css_selector("td:first-child a").get_attribute("innerHTML")
                if (year in yearsToUse):
                    #print(row.get_attribute("innerHTML"))
                    wins = row.find_element_by_css_selector("td:nth-child(2)").get_attribute("innerHTML").strip()
                    losses = row.find_element_by_css_selector("td:nth-child(3)").get_attribute("innerHTML").strip()
                    if "blue" in wins:
                        wins = filter(str.isdigit, str(wins))
                    if "blue" in losses:
                        losses = filter(str.isdigit, str(losses))
                    #print("team: " + team + ", year: " + year + ", wins: " + wins + ", losses: " + losses)
                    if year in records:
                        records[year][team] = wins + "," + losses
                    else:
                        records[year] = {}
                        records[year][team] = wins + "," + losses

            except:
                #print('couldnt find')
                continue
        #print(records)
        #WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.NAME, "2017")))
        browser.close()
        #print("Done!")
    #except:
    #    browser.close()

    with open("./data/teams/records.json", "w") as file:
         json.dump(records, file, sort_keys=True, indent=4)

    for year, yearRecords in records.iteritems():
        with open("./data/teams/records"+str(year)+".csv","w") as file:
            file.write("Team,Wins,Losses\n")
            for team, winsLosses in yearRecords.iteritems():
                file.write(team + "," + winsLosses+"\n")

    #browser.close()

def ConvertTeamNames(teamName):
    if teamName == "Brigham Young":
        teamName = "BYU"
    elif teamName == "Central Florida":
        teamName = "UCF"
    elif teamName == "Hawaii":
        teamName = "Hawai'i"
    elif teamName == "Kent":
        teamName = "Kent State"
    elif teamName == "Louisiana State":
        teamName = "LSU"
    elif teamName == "Miami-Ohio":
        teamName = "Miami (Ohio)"
    elif teamName == "Miami-Florida":
        teamName = "Miami (Florida)"
    elif teamName == "Middle Tennessee State":
        teamName = "Middle Tennessee"
    elif teamName == "Nevada-Las Vegas":
        teamName = "UNLV"
    elif teamName == "Nevada-Reno":
        teamName = "Nevada"
    elif teamName == "Southern Cal":
        teamName = "USC"
    elif teamName == "Southern Methodist":
        teamName = "SMU"
    elif teamName == "Southern Miss":
        teamName = "Southern Mississippi"
    elif teamName == "Texas A+M":
        teamName = "Texas A&M"
    elif teamName == "Texas-El Paso":
        teamName = "UTEP"
    elif teamName == "Texas Christian":
        teamName = "TCU"
    elif teamName == "Texas Christian":
        teamName = "TCU"
    elif teamName == "Texas Christian":
        teamName = "TCU"
    elif teamName == "Texas Christian":
        teamName = "TCU"
    elif teamName == "Texas Christian":
        teamName = "TCU"
    elif teamName == "UMass":
        teamName = "Massachusetts"

    return teamName

if __name__ == "__main__":
    main()
