import json
import os
import glob
import argparse
import math
from ImportFiles import SelectColumnsFromMultipleFiles

teamFiles = glob.glob("./data/teams/team*.csv")
teamColumns = ["Team Code","Year", "Conference Code", "Wins", "Losses", "Name"]
teamYears = SelectColumnsFromMultipleFiles(teamFiles, teamColumns)

print(teamYears.head())
code1 = teamYears.loc[teamYears['Name'] == "Boston College", 'Conference Code'].iloc[0]
code2 = teamYears.loc[teamYears['Name'] == "Notre Dame", 'Conference Code'].iloc[0]
print(code1)
print(code2)
teamYearInfo = {}
conferenceInfo = {}

# for index, team in teamYears.iterrows():
#     if team['Team Code'] not in teamYearInfo:
#         teamYearInfo[team['Team Code']] = {}
#     teamYearInfo[team['Team Code']][team['Year']] = {'Conference Code':team['Conference Code'], 'Wins': 0 if math.isnan(team['Wins']) else team['Wins'], 'Losses': 10 if math.isnan(team['Losses']) else team['Losses']}
#     conferenceInfo[team['Team Code']] = {'Conference Code':team['Conference Code'], 'Name': team['Name']}
#
# with open("./data/team_conference.json", "w") as file:
#     json.dump(conferenceInfo, file, sort_keys=True, indent=4)
