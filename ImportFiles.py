import pandas as pd
import csv
import numpy as np

def SelectColumnsFromMultipleFiles(fileNames, columnNames, dataTypes = {}):
    fullContents = []
    for file in fileNames:
        currentContents = pd.read_csv(file, header = 0, usecols=columnNames, dtype = dataTypes)
        fullContents.append(currentContents)

    return pd.concat(fullContents)

def SelectColumnsFromMultipleFilesFiltered(fileNames, columnNames, comparePosition, compareValue):
    fullContents = []
    for file in fileNames:
        currentContents = pd.read_csv(file, header = 0, usecols=columnNames)
        fullContents.append(currentContents.loc[currentContents[columnNames[comparePosition]] <= compareValue])

    return pd.concat(fullContents)

def SelectColumnsFromMultipleFilesFilteredIn(fileNames, columnNames, comparePosition, compareValues):
    fullContents = []
    for file in fileNames:
        currentContents = pd.read_csv(file, header = 0, usecols=columnNames)
        fullContents.append(currentContents.loc[currentContents[columnNames[comparePosition]].isin(compareValues)])

    return pd.concat(fullContents)

def SelectColumnsFromMultipleFilesRemoveDuplicates(fileNames, columnNames, indexColumn):
    fullContents = []
    for file in fileNames:
        currentContents = pd.read_csv(file, header = 0, usecols=columnNames)
        fullContents.append(currentContents)

    #df.apply(lambda x: x.fillna(x.mean()),axis=0)
    return pd.concat(fullContents).drop_duplicates(subset=indexColumn, keep="last").reset_index(drop=True)

# def GetSituation():
#     return situation
