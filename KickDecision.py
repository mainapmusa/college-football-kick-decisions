from ExpectedPoints import ExpectedPointsByStartPosition
from ExpectedPoints import GraphExpectedPointsByStartPositionFullField
from ExpectedPoints import GraphExpectedPointsByStartPosition
from ExpectedPoints import GraphTeamPointsPerPossessionByYear
from ExpectedPoints import GraphCompareTeamsPointsPerPossession
from ExpectedPoints import GraphCompareConferencePointsPerPossession
from ExpectedPoints import TopPointsPerPossession
from ExpectedPoints import PointsPerPossessionForTeamForYear
from GoOn4th import GoOn4thSuccessPredictionLogisticRegression
from GoOn4th import GraphKnnGoOn4thAccuracy
from GoOn4th import GraphLogisticRegressionGoOn4thAccuracy
from FieldGoals import FieldGoalExpectedValueLogisticRegression
from FieldGoals import FieldGoalExpectedValueKnn
from FieldGoals import GraphFieldGoalPercentByDistance
from FieldGoals import GraphKnnFieldGoalAccuracy
from FieldGoals import GraphNaiveBayesFieldGoalAccuracy
from FieldGoals import GraphGaussianProcessFieldGoalAccuracy
from FieldGoals import GraphRandomForestFieldGoalAccuracy
from FieldGoals import GraphLogisticRegressionFieldGoalAccuracy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import argparse
from SendTweet import tweet
import os
from sys import exit
#from ImportFiles import GetSituation

def main():
    helpStrings = GetHelpStrings()
    parser = argparse.ArgumentParser()

    parser.add_argument("-Situation", help=helpStrings["Situation"], nargs='+', type=int)
    parser.add_argument("-Teams", help=helpStrings["Teams"], nargs='+', type=str)
    parser.add_argument("-Conferences", help=helpStrings["Conferences"], nargs='+', type=str)
    parser.add_argument("-tweet", help=helpStrings["tweet"], action='store_true', default=False)
    parser.add_argument("-GetFieldGoalDecision", help=helpStrings["GetFieldGoalDecision"], action='store_true', default=False)
    parser.add_argument("-Graph4thAndDistance", help=helpStrings["Graph4thAndDistance"], action='store_true', default=False)
    parser.add_argument("-GraphTeamPointsPerPossessionByYear", help=helpStrings["GraphTeamPointsPerPossessionByYear"], action='store_true', default=False)
    parser.add_argument("-GraphCompareConferencePointsPerPossession", help=helpStrings["GraphCompareConferencePointsPerPossession"], action='store_true', default=False)
    args = parser.parse_args()
    print args
    #set up plot design
    plt.xkcd()

    #"End Period", "End Clock", "End Spot"
    #"4 Play Number", "1 Period Number", "5 Offense Points", "6 Defense Points", "7 Distance", "3 Spot", "8 Play Type", "9 Drive Number", "10 Drive Play"
    #"1 Period, 2 SecondsLeft, 3 Spot, 4 PlayNumber, 5 OffensePoints, 6 DefensePoints, 7 Distance, 8 PlayType, 9 DriveNumber, 10 DrivePlay"
    if(args.GetFieldGoalDecision):
        if(len(args.Situation)) != 10:
            exit("If getting a field goal decision must pass the situation for which you are investigating with the -Situation parameter:\n" + helpStrings["Situation"])

        fgSituation = args.Situation[:3]
        g4Situation = [args.Situation[3]] + [args.Situation[0]] + args.Situation[4:7] + [args.Situation[2]] + args.Situation[7:]

        GetFieldGoalDecision(fgSituation, g4Situation, args.tweet)

    if(args.GraphCompareConferencePointsPerPossession):
        if(len(args.Conferences) == 0):
            exit("Must include list of conferences using -Conferences to compare with -GraphCompareConferencePointsPerPossession")

        GraphCompareConferencePointsPerPossession(conferences = args.Conferences, tweetResults=args.tweet)

    #earlyGameFgs = [2,615]
    #earlyGameGoingForIt = [100, 2, 7, 7, 1, 10, 1]
    #earlyGameGoingForItRunAndPass = [100, 2, 7, 7, 10, 1]


    #GetFieldGoalDecision(fgSituation, g4Situation, args.tweet)
    #Graph4thAndDistance(earlyGameFgs, earlyGameGoingForIt,5)
    #Graph4thAndDistanceRunAndPass(earlyGameFgs, earlyGameGoingForItRunAndPass, 1)

    #imagePath = "./imgs/"+os.listdir("./imgs")[0]
    #tweet("test tweet Saturday")

    #ExpectedPoints
    #GraphExpectedPointsByStartPosition()
    #GraphExpectedPointsByStartPositionFullField()
    #GraphTeamPointsPerPossessionByYear("Oklahoma")
    #GraphTeamPointsPerPossessionByYear("Notre Dame")
    #GraphTeamPointsPerPossessionByYear("Boise State")
    #GraphCompareTeamsPointsPerPossession(["Notre Dame", "Oklahoma", "Syracuse", "Miami (Florida)"])
    #make sure following call works with no conferences list
    #GraphCompareConferencePointsPerPossession()
    #GraphCompareConferencePointsPerPossession(conferences = ["Atlantic Coast Conference", "Southeastern Conference", "Big 12 Conference"])
    #TopPointsPerPossession()
    #print(PointsPerPossessionForTeamForYear("Boise State", 2009))


    #GoOn4th
    #GraphKnnGoOn4thAccuracy(9,True)
    #GraphLogisticRegressionGoOn4thAccuracy(6,True)

    #FieldGoals
    #GraphFieldGoalPercentByDistance()
    #GraphKnnFieldGoalAccuracy(10,True)
    #GraphNaiveBayesFieldGoalAccuracy(5,True)

    #Get working gaussian
    #GraphGaussianProcessFieldGoalAccuracy(3)

    #GraphRandomForestFieldGoalAccuracy(10,True)
    #GraphLogisticRegressionFieldGoalAccuracy(6,True)

def GetFieldGoalDecision(fgSituation, g4Situation, tweetResults = False):
    #"End Period", "End Clock", "End Spot"
    fieldGoalExpectedValue = FieldGoalExpectedValueKnn(fgSituation,True)

    #"Play Number", "Period Number", "Offense Points", "Defense Points", "Distance", "Spot", "Play Type", "Drive Number", "Drive Play"
    goOn4thSuccessPrediction = GoOn4thSuccessPredictionLogisticRegression(g4Situation)

    #Spot - Distance OR 7 if Spot - Distance == 0
    conversionStartingSpot = g4Situation[5]-g4Situation[4]

    expectedPoints = ExpectedPointsByStartPosition(conversionStartingSpot) if conversionStartingSpot > 0 else 7
    overallExpectedPoints = goOn4thSuccessPrediction*expectedPoints

    decisionValues = (fieldGoalExpectedValue, goOn4thSuccessPrediction, expectedPoints, overallExpectedPoints)
    if(tweetResults == True):
        TweetDecision(decisionValues, conversionStartingSpot)

    return decisionValues

def TweetDecision(decisionValues, conversionStartingSpot):
    message = ""
    message += "Field Goal Expected Value: "+str(decisionValues[0])+"\n"
    message += "4th Down Conversion Likelihood: "+str(decisionValues[1])+"\n"
    message += "Line To Reach For Conversion: "+str(conversionStartingSpot)+"\n"
    message += "Expected Points For Starting From Converstion Spot: "+str(decisionValues[2])+"\n"

    message += "Expected Value Of Going For It: " + str(decisionValues[3])+"\n"

    if (decisionValues[3] > decisionValues[0]):
        message += "GO FOR IT!"
    else:
        message += "KICK THE FIELD GOAL!"

    print(message)
    imagePath = "./imgs/temp_image.png"
    teams = ('Kick Field Goal', 'Go For It')
    y_pos = np.arange(len(teams))
    expectedPoints = [decisionValues[0], decisionValues[3]]

    plt.bar(y_pos, expectedPoints, align='center', alpha=0.5)
    plt.xticks(y_pos, teams)
    plt.title("Expected Points of Field Goal vs Going for it on 4th")
    #plt.xlabel("Teams")
    plt.ylabel("Expected Points")
    plt.savefig(imagePath)

    tweet(message,imagePath)

def Graph4thAndDistanceRunAndPass(fgSituation, g4Situation, distance):
    attemptsRun = []
    attemptsPass = []
    for spot in range(distance, 36):
        fgSituationCurrent = fgSituation + [spot]
        g4SituationCurrentPass = g4Situation[:4] + [distance, spot, 0] + g4Situation[4:]
        g4SituationCurrentRun = g4Situation[:4] + [distance, spot, 1] + g4Situation[4:]

        attemptsRun.append(GetFieldGoalDecision(fgSituationCurrent, g4SituationCurrentRun, False))
        attemptsPass.append(GetFieldGoalDecision(fgSituationCurrent, g4SituationCurrentPass, False))

    attemptsRun = pd.DataFrame(attemptsRun)
    attemptsPass = pd.DataFrame(attemptsPass)

    #attempts = attemptsRun.join(attemptsPass[3])
    #attempts[5] = attempts[[3, 4]].max(axis=1)
    #plt.plot(attempts[0])
    #plt.plot(attempts[5])

    plt.plot(attemptsRun[0])
    plt.plot(attemptsRun[3])
    plt.plot(attemptsPass[3])

    plt.legend(["FG Expected Value","Rush For 4th and " + str(distance)+ " Expected Value","Pass For 4th and " + str(distance)+ " Expected Value"])
    plt.title("Qtr: " + str(fgSituation[0]) + ", Time left: " + str(time.strftime("%M:%S",time.gmtime(fgSituation[1])))+ ", Offense points: " + str(g4Situation[2]) + ", Defense points: " +str(g4Situation[3]))
    plt.xlabel("Yard Line")
    plt.ylabel("Expected Points")
    plt.show()
    #takes in arrays but g4Situation is missing distance and Spot
    #loop through while injecting 4th and 1
    #get fieldGoalExpectedValue and overallExpectedPoints for each and add to arrays
    #line graph for arrays, view shape
    #do for both rushing and passing

def Graph4thAndDistance(fgSituation, g4Situation, distance):
    attempts = []
    for spot in range(distance, 36):
        fgSituationCurrent = fgSituation + [spot]
        g4SituationCurrent = g4Situation[:4] + [distance, spot] + g4Situation[4:]
        attempts.append(GetFieldGoalDecision(fgSituationCurrent, g4SituationCurrent, False))

    attempts = pd.DataFrame(attempts)
    plt.plot(attempts[0])
    plt.plot(attempts[3])

    plt.legend(["FG Expected Value","Go For 4th and " + str(distance)+ " Expected Value"])
    plt.title("Qtr: " + str(fgSituation[0]) + ", Time left: " + str(time.strftime("%M:%S",time.gmtime(fgSituation[1])))+ ", Offense points: " + str(g4Situation[2]) + ", Defense points: " +str(g4Situation[3]))
    plt.xlabel("Yard Line")
    plt.ylabel("Expected Points")
    plt.savefig("./imgs/CompareGo4thVsKickFieldGoalDistance"+str(distance)+".png")
    plt.show()
    tweet("test tweet during pre-prod deployment","./imgs/CompareGo4thVsKickFieldGoalDistance"+str(distance)+".png")
    #takes in arrays but g4Situation is missing distance and Spot
    #loop through while injecting 4th and 1
    #get fieldGoalExpectedValue and overallExpectedPoints for each and add to arrays
    #line graph for arrays, view shape
    #do for both rushing and passing

def GetHelpStrings():
    helpStrings = {}
    helpStrings["tweet"] = "Include this flag to tweet out via TBM"
    helpStrings["Situation"] = "Period, SecondsLeft, Spot, PlayNumber, OffensePoints, DefensePoints, Distance, PlayType, DriveNumber, DrivePlay"
    helpStrings["Teams"] = "Team(s) to be used"
    helpStrings["Conferences"] = "Conference(s) to be used"
    helpStrings["GetFieldGoalDecision"] = "Pass situation to get kick decision, and optional true if you want results printed" #(fgSituation, g4Situation, True)
    helpStrings["Graph4thAndDistance"] = "Pass situation to graph expected points of going for it vs kicking at that distance" #(earlyGameFgs, earlyGameGoingForIt,5)
    helpStrings["Graph4thAndDistanceRunAndPass"] = "Pass situation to graph expected points of going for it vs kicking at that distance for both rushing and passing" #(earlyGameFgs, earlyGameGoingForItRunAndPass, 1)
    helpStrings["GraphExpectedPointsByStartPosition"] = "See graph of expected points for starting any point inside 35"
    helpStrings["GraphExpectedPointsByStartPositionFullField"] = "See graph of expected points for starting any point on the field"
    helpStrings["GraphTeamPointsPerPossessionByYear"] = "Pass in team name to see points per possession for each year in dataset"
    helpStrings["GraphCompareTeamsPointsPerPossession"] = "Pass in list of teams to see points per possession for each year in dataset"
    #make sure following call works with no conferences list
    helpStrings["GraphCompareConferencePointsPerPossession"] = "Pass in list of conferences to see points per possession for each compared" #= (conferences = ["Atlantic Coast Conference", "Southeastern Conference", "Big 12 Conference"])
    helpStrings["TopPointsPerPossession"] = "List teams over dataset that high highest points per possession"
    helpStrings["PointsPerPossessionForTeamForYear"] = "Pass team and year to get print out of their points per possession"
    helpStrings["GraphKnnGoOn4thAccuracy"] = "See graph of accuracy of k-NN model for going on 4th down when using up to a passed in number of neighbors"
    helpStrings["GraphLogisticRegressionGoOn4thAccuracy"] = "See graph of accuracy of logistic regression for going on 4th down with up to a passed in number of C values"
    helpStrings["GraphFieldGoalPercentByDistance"] = "See graph of field goal % by field position"
    helpStrings["GraphKnnFieldGoalAccuracy"] = "Graph field goal accuracy using k-NN with up to a passed in number of neighbors"
    helpStrings["GraphNaiveBayesFieldGoalAccuracy"] = "Graph field goal accuracy using Naive Bayes with up to a passed in number of alphas"
    helpStrings["GraphGaussianProcessFieldGoalAccuracy"] = "Graph field goal accuracy using Gaussian with up to a passed in number of kernals"

    helpStrings["GraphRandomForestFieldGoalAccuracy"] = "Graph field goal accuracy using random forest with up to a passed in number of estimators"
    helpStrings["GraphLogisticRegressionFieldGoalAccuracy"] = "Graph field goal accuracy using logistic regression with up to a passed in number of C values"

    return helpStrings

if __name__ == "__main__":
    main()
