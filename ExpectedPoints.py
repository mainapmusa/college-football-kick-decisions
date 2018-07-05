import pandas as pd
import csv
import numpy as np
from sklearn.externals import joblib
import os.path
import matplotlib.pyplot as plt
import glob
from ImportFiles import SelectColumnsFromMultipleFiles
from ImportFiles import SelectColumnsFromMultipleFilesFiltered
from ImportFiles import SelectColumnsFromMultipleFilesFilteredIn
from ImportFiles import SelectColumnsFromMultipleFilesRemoveDuplicates
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import f_regression
from sklearn.metrics import classification_report
#sklearn.svm.LinearSVC
#from sas7bdat import SAS7BDAT

#sudo pip install pandas

def GetFiles():
    driveFiles = glob.glob("./data/drives/drive*.csv")
    teamFiles = glob.glob("./data/teams/team*.csv")
    conferenceFiles = glob.glob("./data/conferences/conference*.csv")
    return driveFiles, teamFiles, conferenceFiles

def GetPoints():
    driveFiles = GetFiles()[0]
    drivesInside35 = SelectColumnsFromMultipleFilesFiltered(driveFiles, ["Start Spot", "End Reason"], 0, 35)
    points = {}
    driveCounts = drivesInside35["Start Spot"].value_counts()
    for i, drive in drivesInside35.iterrows():
        if drive["Start Spot"] in points:
            points[drive["Start Spot"]] += 7.0 if drive["End Reason"] == "TOUCHDOWN" else 3.0 if drive["End Reason"] == "FIELD GOAL" else 0.0
        else:
            points[drive["Start Spot"]] = 7.0 if drive["End Reason"] == "TOUCHDOWN" else 3.0 if drive["End Reason"] == "FIELD GOAL" else 0.0

    for key, value in points.items():
        points[key] = round(points[key]/driveCounts[key],3)

    return points

#potential things to add teams and home/away from game.csv+team.csv+conference.csv and added wins data
#http://football.stassen.com/cgi-bin/records/show-team.pl

def GetDrivesWithConference():
    driveFiles, teamFiles, conferenceFiles = GetFiles()
    drives = SelectColumnsFromMultipleFiles(driveFiles, ["Team Code", "Start Period", "Start Clock", "Start Reason" ,"Start Spot", "End Reason", "Plays", "Yards", "Time Of Possession", "Year"])
    teams = SelectColumnsFromMultipleFilesRemoveDuplicates(teamFiles,["Team Code", "Name", "Conference Code","Wins"], "Team Code")
    conferences = SelectColumnsFromMultipleFilesRemoveDuplicates(conferenceFiles,["Conference Code", "Name", "Subdivision"], "Conference Code")

    drivesWithTeam = pd.merge(drives, teams, how = "left", on = ["Team Code"])
    drivesWithConference = pd.merge(drivesWithTeam, conferences, how = "left", on = ["Conference Code"])

    drivesWithConference.rename(columns = {"Name_x": "Team Name", "Name_y": "Conference Name"}, inplace = True)
    drivesWithConference["End Reason"].replace(["TOUCHDOWN", "FIELD GOAL", "DOWNS", "END OF HALF", "FUMBLE", "INTERCEPTION", "MISSED FIELD GOAL", "PUNT", "SAFETY"], [7, 3, 0, 0, 0, 0, 0, 0, 0], inplace=True)

    return drivesWithConference

def ExpectedPointsByStartPosition(startPosition):
    points = GetPoints()
    return points[startPosition]

def GraphExpectedPointsByStartPosition():
    points = GetPoints()
    plt.plot(*zip(*sorted(points.items())))
    plt.title("Expected Value vs Starting Field Position")
    plt.legend()
    plt.xlabel("Starting Field Position")
    plt.ylabel("Expected Points to Score")
    plt.savefig("./imgs/ExpectedPointsByStartPosition.png")
    plt.show()


def GraphExpectedPointsByStartPositionFullField():
    driveFiles = GetFiles()[0]
    drivesFullField = SelectColumnsFromMultipleFiles(driveFiles, ["Start Spot", "End Reason"])
    pointsFullField = {}
    driveCountsFullField = drivesFullField["Start Spot"].value_counts()
    for i, drive in drivesFullField.iterrows():
        if drive["Start Spot"] in pointsFullField:
            pointsFullField[drive["Start Spot"]] += 7.0 if drive["End Reason"] == "TOUCHDOWN" else 3.0 if drive["End Reason"] == "FIELD GOAL" else 0.0
        else:
            pointsFullField[drive["Start Spot"]] = 7.0 if drive["End Reason"] == "TOUCHDOWN" else 3.0 if drive["End Reason"] == "FIELD GOAL" else 0.0

    for key, value in pointsFullField.items():
        pointsFullField[key] = round(pointsFullField[key]/driveCountsFullField[key],3)
    plt.plot(*zip(*sorted(pointsFullField.items())))
    plt.title("Expected Value vs Starting Field Position")
    plt.legend()
    plt.xlabel("Starting Field Position")
    plt.ylabel("Expected Points to Score")
    plt.savefig("./imgs/ExpectedPointsByStartPositionFullField.png")
    plt.show()

def ExpectedPointsByStartPositionLogisticRegression(situation):
    return True

def PointsPerPossessionForTeamForYear(teamName, year):
    drivesWithConference = GetDrivesWithConference()
    teamsDrives = drivesWithConference.loc[(drivesWithConference["Team Name"] == teamName) & (drivesWithConference["Year"] == year)]
    #teamsDrives["End Reason"].replace(["TOUCHDOWN", "FIELD GOAL", "DOWNS", "END OF HALF", "FUMBLE", "INTERCEPTION", "MISSED FIELD GOAL", "PUNT", "SAFETY"], [7, 3, 0, 0, 0, 0, 0, 0, 0], inplace=True)
    yearPPP = pd.DataFrame(teamsDrives.groupby(["Year"])["End Reason"].mean())
    return yearPPP.iloc[0,0]

def GraphTeamPointsPerPossessionByYear(teamName):
    drivesWithConference = GetDrivesWithConference()
    teamsDrives = drivesWithConference.loc[drivesWithConference["Team Name"] == teamName]
    #teamsDrives["End Reason"].replace(["TOUCHDOWN", "FIELD GOAL", "DOWNS", "END OF HALF", "FUMBLE", "INTERCEPTION", "MISSED FIELD GOAL", "PUNT", "SAFETY"], [7, 3, 0, 0, 0, 0, 0, 0, 0], inplace=True)

    yearPPP = pd.DataFrame(teamsDrives.groupby(["Year"])["End Reason"].mean())
    yearPPP["Year"] = yearPPP.index.values

    plt.plot(yearPPP["Year"],yearPPP["End Reason"])
    plt.xticks(yearPPP["Year"])
    #plt.axis([2005,2013,0,7])
    plt.title(teamName +" Points per Possession 2005-2013")
    plt.xlabel("Year")
    plt.ylabel("Points Per Possession")
    plt.savefig("./imgs/"+teamName+"PointsPerPossesion"+".png")
    plt.show()
    #print(teamsDrives.head(10))

def GraphCompareTeamsPointsPerPossession(teams):
    drivesWithConference = GetDrivesWithConference()
    teamsPPPs = []
    plt.figure(figsize=(14,8))
    for team in teams:
        drives = drivesWithConference.loc[drivesWithConference["Team Name"] == team]
        ppp = pd.DataFrame(drives.groupby(["Year"])["End Reason"].mean())
        ppp["Year"] = ppp.index.values

        plt.plot(ppp["Year"], ppp["End Reason"])

    plt.title("Comparison of "+str(len(teams))+" teams")
    plt.xlabel("Year")
    plt.ylabel("Points Per Possession")
    plt.legend(teams)
    #plt.axis.XAxis(["2005","2006","2007","2008","2009","2010","2011","2012","2013"])
    #plt.set_xticklabels(["2005","2006","2007","2008","2009","2010","2011","2012","2013"])
    plt.show()


def GraphCompareConferencePointsPerPossession(filters = {}, conferences = []):
    drivesWithConference = GetDrivesWithConference()
    confDrives = drivesWithConference[["Team Name","Conference Name","End Reason", "Year", "Subdivision"]]
    for key, value in filters.items():
        confDrives = confDrives.loc[confDrives[key] == value]

    confDrives = confDrives.loc[confDrives["Conference Name"].isin(conferences)]

    confDrives["Conference Name"] = confDrives["Conference Name"].map(lambda x: x.rstrip("Conference"))
    confPPP = pd.DataFrame(confDrives.groupby(["Conference Name"])["End Reason"].mean())
    #confPPP["Conference Name"] = confPPP.index.values

    #print(confPPP)
    #plt.plot(confPPP)
    confPPP.plot(kind="bar",figsize=(18,10), legend=None)
    plt.subplots_adjust(bottom=0.2)
    plt.title("Points per Possession for Conferences")
    plt.savefig("./imgs/ConferencesPointsPerPossesion"+".png")
    plt.show()

def TopPointsPerPossession():
    drivesWithConference = GetDrivesWithConference()
    #allDrives = drivesWithConference[["Team Name", "Year", "End Reason"]]
    allDrives = drivesWithConference.loc[drivesWithConference["Subdivision"] == "FBS"][["Team Name", "Year", "End Reason"]]

    #allDrives["End Reason"].replace(["TOUCHDOWN", "FIELD GOAL", "DOWNS", "END OF HALF", "FUMBLE", "INTERCEPTION", "MISSED FIELD GOAL", "PUNT", "SAFETY"], [7, 3, 0, 0, 0, 0, 0, 0, 0], inplace=True)
    teamsPPP = pd.DataFrame(allDrives.groupby(["Team Name", "Year"])["End Reason"].mean())
    teamsPPP.rename(columns = {"End Reason": "Points Per Possession"}, inplace = True)
    print(teamsPPP.sort_values(["Points Per Possession"], ascending=False).head(25))
