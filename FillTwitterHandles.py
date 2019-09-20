import json
import os
import argparse
import glob
from ImportFiles import SelectColumnsFromMultipleFiles

teamFiles = glob.glob("./data/teams/team*.csv")
teamColumns = ["Team Code","Year", "Conference Code", "Wins", "Losses", "Name"]
teamYears = SelectColumnsFromMultipleFiles(teamFiles, teamColumns)

with open("./data/espn_ids.json") as data_file:
      espnInfo = json.load(data_file)

#for team in espnInfo:
#    espnInfo[team]["TwitterHandles"] = espnInfo[team]["Name"]

#for team in espnInfo:
#    espnInfo[team]["Hashtags"] = "#"+espnInfo[team]["Name"].replace(" ","")

for team in espnInfo:
    #print(team)
    try:
        code = teamYears.loc[teamYears['Name'] == espnInfo[team]["Name"], 'Conference Code'].iloc[0]
    except:
        code = 99001
    #print(code)
    espnInfo[team]["Conference Code"] = str(code)
    #print(espnInfo[team])

#print(espnInfo)

with open("./data/espn_ids.json", "w") as file:
    json.dump(espnInfo, file, sort_keys=True, indent=4)
