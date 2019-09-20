import pandas as pd
import csv
import numpy as np
from sklearn.externals import joblib
import os.path
import matplotlib.pyplot as plt
import glob
from ImportFiles import SelectColumnsFromMultipleFiles
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.feature_selection import f_regression
from sklearn.metrics import classification_report

#sklearn.svm.LinearSVC
#from sas7bdat import SAS7BDAT

#sudo pip install pandas

#from play: Game Code, Play Number, Period Number, Offense Points, Defense Points, Down, Distance, Spot, Play Type, Drive Number, Drive Play
#from rush: Game Code, Play Number, Team Code*, Player Code*, Attempt*, Yards, Touchdown, 1st Down
#from pass: Game Code, Play Number, Team Code*, Passer Player Code*, Receiver Player Code*, Attempt*, Yards, Touchdown, 1st Down

def GetTestAndTrainSets():
    playFiles = glob.glob("./data/plays/*.csv")
    rushFiles = glob.glob("./data/rushes/*.csv")
    passFiles = glob.glob("./data/passes/*.csv")
    teamFiles = glob.glob("./data/teams/team*.csv")

    playColumns = ["Game Code", "Play Number", "Period Number", "Offense Points", "Defense Points", "Down", "Distance", "Spot", "Play Type", "Drive Number", "Drive Play", "Offense Team Code", "Defense Team Code", "Year"]
    rushPassColumns = ["Game Code", "Play Number", "Attempt", "Yards", "Touchdown", "1st Down"]
    teamColumns = ["Team Code","Year", "Conference Code", "Wins", "Losses"]

    plays = SelectColumnsFromMultipleFiles(playFiles, playColumns,{"Game Code": np.str})
    plays["Game Code"] = plays["Game Code"].str.zfill(16)
    rushes = SelectColumnsFromMultipleFiles(rushFiles, rushPassColumns,{"Game Code": np.str, "Touchdown":np.bool,"1st Down":np.bool}) #, "Touchdown":np.bool,"1st Down":np.bool
    rushes["Game Code"] = rushes["Game Code"].str.zfill(16)
    passes = SelectColumnsFromMultipleFiles(passFiles, rushPassColumns,{"Game Code": np.str, "Touchdown":np.bool,"1st Down":np.bool})
    passes["Game Code"] = passes["Game Code"].str.zfill(16)


    fourthDownAttempts = plays.loc[(plays["Down"] == 4) & ((plays["Play Type"] == "RUSH") | (plays["Play Type"] == "PASS"))]

    fourthRushes = pd.merge(fourthDownAttempts.loc[fourthDownAttempts["Play Type"] == "RUSH"], rushes, how = "left", on = ["Game Code", "Play Number"])
    fourthPasses = pd.merge(fourthDownAttempts.loc[fourthDownAttempts["Play Type"] == "PASS"], passes, how = "left", on = ["Game Code", "Play Number"])

    fourthDownAttempts = pd.concat([fourthRushes,fourthPasses])

    teams = SelectColumnsFromMultipleFiles(teamFiles, teamColumns)
    # The wins and losses are N/A when the team is FCS so I'm treating those as 0-10 teams since they're almost all much less skilled than FBS teams
    teams.fillna({"Wins":0,"Losses":10}, inplace=True)

    fourthDownAttempts = pd.merge(fourthDownAttempts, teams, how = "left", left_on = ["Offense Team Code", "Year"], right_on = ["Team Code", "Year"])

    fourthDownAttempts = pd.merge(fourthDownAttempts, teams, how = "left", left_on = ["Defense Team Code", "Year"], right_on = ["Team Code", "Year"])

    fourthDownAttempts["Play Type"].replace(["RUSH", "PASS"], [1, 0], inplace=True)

    fourthDownAttempts["Convert"] = fourthDownAttempts["Touchdown"] | fourthDownAttempts["1st Down"]

    fourthDownAttempts.drop(["Game Code", "Touchdown","1st Down", "Attempt", "Down", "Yards"], axis=1, inplace = True)

    fourthDownAttempts.rename(columns={'Wins_x': 'Offense Wins','Wins_y': 'Defense Wins','Losses_x': 'Offense Losses','Losses_y': 'Defense Losses','Conference Code_x': 'Offense Conference','Conference Code_y': 'Defense Conference'}, inplace=True)


    fourthDownAttempts['Offense Conference Rank'] = fourthDownAttempts['Offense Conference'].apply(GetConferenceStrength)
    fourthDownAttempts['Defense Conference Rank'] = fourthDownAttempts['Defense Conference'].apply(GetConferenceStrength)
    fourthDownAttempts = fourthDownAttempts[["Convert","Play Number", "Period Number", "Offense Points", "Defense Points", "Distance", "Spot", "Play Type", "Drive Number", "Offense Wins", "Offense Losses",  "Offense Conference Rank", "Defense Wins", "Defense Losses", "Defense Conference Rank"]]
    #fourthDownAttempts = fourthDownAttempts.drop(['Team Code_x','Team Code_y', 'Drive Play', 'Year', 'Offense Team Code', 'Defense Team Code', 'Offense Conference', 'Defense Conference'], axis=1)

    #fourthDownAttempts = pd.get_dummies(fourthDownAttempts, columns=['Offense Conference','Defense Conference'])

    fourthDownAttempts.to_csv("./data/go_final.csv")
    y = fourthDownAttempts["Convert"].values
    X = fourthDownAttempts.drop("Convert", axis=1).values

    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=42, stratify=y)
    return train_test_split(X, y, test_size = 0.2, random_state=42, stratify=y)

def ModelExistence(usePersistedModel, filename):
    currentModelExists = True
    if usePersistedModel:
        if not os.path.isfile(filename):
            print(filename+" does not exist so model being created and saved")
            currentModelExists = False
    return currentModelExists

def GoOn4thSuccessPredictionLogisticRegression(situation, usePersistedModel = False):
    pd.options.mode.chained_assignment = None
    filename = "./models/GoOn4thSuccessPredictionLogisticRegression.sav"
    currentModelExists = ModelExistence(usePersistedModel,filename)


    if (not usePersistedModel) or (not currentModelExists):
        X_train, X_test, y_train, y_test = GetTestAndTrainSets()
        logistic = LogisticRegression(C=10000)
        LogisticRegression(C=100000.0, class_weight=None, dual=False, fit_intercept=True, intercept_scaling=1, max_iter=100, multi_class="ovr", n_jobs=1, penalty="l2", random_state=None, solver="liblinear", tol=0.0001, verbose=0, warm_start=False)

        logistic.fit(X_train, y_train)
        #persist model
        joblib.dump(logistic, filename)
    else:
        logistic = joblib.load(filename)

    prediction = logistic.predict_proba(np.asarray(situation).reshape(1,-1))[:,1]
    return prediction[0]

def GraphKnnGoOn4thAccuracy(neighborsCount, usePersistedModel = False):
    # Setup arrays to store train and test accuracies
    neighbors = np.arange(1, neighborsCount)
    train_accuracy = np.empty(len(neighbors))
    test_accuracy = np.empty(len(neighbors))
    X_train, X_test, y_train, y_test = GetTestAndTrainSets()

    # Loop over different values of k
    for i, k in enumerate(neighbors):
        filename = "./models/GraphKnnGoOn4thAccuracy_"+str(k)+".sav"
        currentModelExists = ModelExistence(usePersistedModel,filename)

        if (not usePersistedModel) or (not currentModelExists):
            # Setup a k-NN Classifier with k neighbors: knn
            knn = KNeighborsClassifier(n_neighbors=k)

            # Fit the classifier to the training data
            knn.fit(X_train, y_train)

            #persist model
            joblib.dump(knn, filename)
        else:
            knn = joblib.load(filename)

        #Compute accuracy on the training set
        train_accuracy[i] = knn.score(X_train, y_train)

        #Compute accuracy on the testing set
        test_accuracy[i] = knn.score(X_test, y_test)

    # Generate plot
    plt.title("Going on 4th k-NN: Varying Number of Neighbors")
    plt.plot(neighbors, test_accuracy, label = "Testing Accuracy")
    plt.plot(neighbors, train_accuracy, label = "Training Accuracy")
    plt.legend()
    plt.xlabel("Number of Neighbors")
    plt.ylabel("Accuracy")
    plt.savefig("./imgs/Go4thKnn"+str(neighborsCount)+"Neighbors.png")
    plt.show()

def GraphLogisticRegressionGoOn4thAccuracy(maxC, usePersistedModel = False):
    Cs = np.arange(1, maxC)
    train_accuracy2 = np.empty(len(Cs))
    test_accuracy2 = np.empty(len(Cs))
    X_train, X_test, y_train, y_test = GetTestAndTrainSets()

    # Loop over different values of C
    for i, c in enumerate(Cs):
        filename = "./models/GraphLogisticRegressionGoOn4thAccuracy_"+str(10**c)+".sav"
        currentModelExists = ModelExistence(usePersistedModel,filename)

        if (not usePersistedModel) or (not currentModelExists):
            # Setup a k-NN Classifier with k neighbors: knn
            logistic = LogisticRegression(C=10**c)

            # Fit the classifier to the training data
            logistic.fit(X_train, y_train)

            #persist model
            joblib.dump(logistic, filename)
        else:
            logistic = joblib.load(filename)

        #Compute accuracy on the training set
        train_accuracy2[i] = logistic.score(X_train, y_train)

        #Compute accuracy on the testing set
        test_accuracy2[i] = logistic.score(X_test, y_test)

    # Generate plot
    plt.title("Going on 4th Logistic Regression: Varying value of C")
    plt.plot(Cs, test_accuracy2, label = "Testing Accuracy")
    plt.plot(Cs, train_accuracy2, label = "Training Accuracy")
    plt.legend()
    plt.xlabel("C = 10^x")
    plt.ylabel("Accuracy")
    plt.savefig("./imgs/Go4thLogisticRegression"+str(maxC)+"MaxC.png")
    plt.show()

def GetConferenceStrength(ConferenceCode):
    #P5 ACC=821, Big12=25354, Big10=827, Pac12=905, SEC=911, BigEast=823
    #G5 Indy=99001, AAC=823, C-USA=24312, MAC=875, MWC=5486, SunBelt=818, WAC=923
    if ConferenceCode in [821,25354,827,905,911,823]:
        return 10
    elif ConferenceCode in [99001,823,24312,875,5486,818,923]:
        return 5
    else:
        return 0
