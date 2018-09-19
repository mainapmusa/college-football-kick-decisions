import json
import os
import argparse

with open("./data/espn_ids.json") as data_file:
      espnInfo = json.load(data_file)

for team in espnInfo:
    espnInfo[team]["TwitterHandles"] = espnInfo[team]["Name"]

with open("./data/espn_ids.json", "w") as file:
    json.dump(espnInfo, file, sort_keys=True, indent=4)
