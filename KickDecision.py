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
from sys import argv
from SendTweet import tweet
#from ImportFiles import GetSituation

def main():
    args = getArgs(argv)
    #set up plot design
    plt.xkcd()

    fgSituation = [3,200,20]
    g4Situation = [100, 3, 20, 21, 3, 5, 1, 10, 1]
    #epSituation = [15]

    earlyGameFgs = [2,615]
    earlyGameGoingForIt = [100, 2, 7, 7, 1, 10, 1]
    earlyGameGoingForItRunAndPass = [100, 2, 7, 7, 10, 1]
    GetFieldGoalDecision(fgSituation, g4Situation, True)
    #Graph4thAndDistance(earlyGameFgs, earlyGameGoingForIt,1)
    #Graph4thAndDistanceRunAndPass(earlyGameFgs, earlyGameGoingForItRunAndPass, 1)

    tweet("test tweet")


    #ExpectedPoints
    GraphExpectedPointsByStartPosition()
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
    #GraphKnnGoOn4thAccuracy(9)
    #GraphLogisticRegressionGoOn4thAccuracy(6)

    #FieldGoals
    #GraphFieldGoalPercentByDistance()
    #GraphKnnFieldGoalAccuracy(10)
    #GraphNaiveBayesFieldGoalAccuracy(5)

    #Get working gaussian
    #GraphGaussianProcessFieldGoalAccuracy(3)

    #GraphRandomForestFieldGoalAccuracy(10)
    #GraphLogisticRegressionFieldGoalAccuracy(6)

def GetFieldGoalDecision(fgSituation, g4Situation, printResults = False):
    #"End Period", "End Clock", "End Spot"
    fieldGoalExpectedValue = FieldGoalExpectedValueKnn(fgSituation)
    #"Play Number", "Period Number", "Offense Points", "Defense Points", "Distance", "Spot", "Play Type", "Drive Number", "Drive Play"
    goOn4thSuccessPrediction = GoOn4thSuccessPredictionLogisticRegression(g4Situation)
    #Spot - Distance OR 7 if Spot - Distance == 0
    conversionStartingSpot = g4Situation[5]-g4Situation[4]
    expectedPoints = ExpectedPointsByStartPosition(conversionStartingSpot) if conversionStartingSpot > 0 else 7
    overallExpectedPoints = goOn4thSuccessPrediction*expectedPoints

    decisionValues = (fieldGoalExpectedValue, goOn4thSuccessPrediction, expectedPoints, overallExpectedPoints)
    if(printResults == True):
        PrintDecision(decisionValues, conversionStartingSpot)

    return decisionValues

def PrintDecision(decisionValues, conversionStartingSpot):
    print("Field Goal Expected Value: "+str(decisionValues[0]))
    print("4th Down Conversion Likelihood: "+str(decisionValues[1]))
    print("Line To Reach For Conversion: "+str(conversionStartingSpot))
    print("Expected Points For Starting From Converstion Spot: "+str(decisionValues[2]))

    print("Expected Value Of Going For It: " + str(decisionValues[3]))

    if (decisionValues[3] > decisionValues[0]):
        print("GO FOR IT!")
    else:
        print("KICK THE FIELD GOAL!")


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
    #takes in arrays but g4Situation is missing distance and Spot
    #loop through while injecting 4th and 1
    #get fieldGoalExpectedValue and overallExpectedPoints for each and add to arrays
    #line graph for arrays, view shape
    #do for both rushing and passing

def getArgs(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts

if __name__ == "__main__":
    main()
