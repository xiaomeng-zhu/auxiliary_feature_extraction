# author: Xiaomeng (Miranda) Zhu
# Date: Apr 15, 2022
# purpose: extracting morphosyntactic features of interest from txt file

import pandas as pd # library for creating dataframes and storing into csv
from functools import reduce # library for combining pandas dataframes


import os

# =============CHANGE ME=================
# sets the working directory of the program to the folder where you store the txt file of the speaker 
os.chdir('/Users/mirandazhu/Desktop/demo') 


speakerID = "DCB_se3_ag2_f_01_1" # corresponds to the name of the txt file that you downloaded
speaker = "DCB_se3_ag2_f_01" # corresponds to the speaker ID in the transcription


# ==========Part 1: establish the tokens that we would like to find==========
txtFileName = speakerID + ".txt"

# to do: extra column for the specific token that is pulled out
# upload the script to the google file

with open(txtFileName) as f:
    lines = f.readlines()
    
    

AA0orAB0 = []
AA0orAB0Iden = ["ain't"]

AA1 = []
AA1Iden = ["'m not", "'s not", "'re not",
           "am not", "is not", "are not",
           "isn't", "aren't"]

"""
AA2 includes positive forms 
i.e. do, do not, don't';
    does, does not, doesn't; 
    have, have not, 've not, haven't;
    has, has not, hasn't;
"""
AA2 = [] 
AA2Iden = [" do ", "do not", "don't" ,
           " does ", "does not", "doesn't",
           " have ", "have not", "'ve not", "haven't",
           " has ", "has not", "hasn't"
           ] # how to differentiate the verb do and the auxiliary do? the verb have the auxiliary have?

AB1 = [] # also include positive forms: did, didn't, did not
AB1Iden = [" did ", "didn't", "did not"]

CO2 = [] # fully expressed copula
CO2Iden = [" is ", " are ", " am "]

# helper functions for checking if the tokens we are looking for is in the string and count how many
def checkCondition(utter, idenList):
    condition = False
    for i in idenList:
        if i in utter:
            condition = True
    return condition

def checkCount(utter, idenList):
    count = 0
    tokens = []
    for i in idenList:
        currentCount = utter.count(i)
        count = count + currentCount
        for j in range(currentCount):
            tokens.append(i)
    return (count,tokens)




# ==========Part 2: extract features of interest from input file=========
speaker_lines = []
for line in lines:
    if (line.split("\t")[1])==speaker:
        speaker_lines.append(line)


for line in speaker_lines:
    utter_original = line.split("\t")[-2] # the original line
    utter = utter_original.lower() # the line in lowercase text for comparison purposes
    stTime = line.split("\t")[-3] # starting time of the line
    
    # the four if-else statements check for four features of interest
    
    if checkCondition(utter,AA0orAB0Iden):
        # check for repeated tokens in one line
        count,tokens = checkCount(utter, AA0orAB0Iden)# count the number of tokens in the current line
        for i in range(count):
            AA0orAB0.append((stTime,utter_original,tokens[i])) # append to the corresponding list
    
    if checkCondition(utter, AA1Iden):

        count,tokens = checkCount(utter,AA1Iden)
        for i in range(count):
            AA1.append((stTime,utter_original,tokens[i]))
    
    if checkCondition(utter, AA2Iden):
        count,tokens = checkCount(utter,AA2Iden)
        for i in range(count):
            AA2.append((stTime,utter_original,tokens[i]))

    if checkCondition(utter, AB1Iden):
        count,tokens = checkCount(utter,AB1Iden)
        for i in range(count):
            AB1.append((stTime,utter_original,tokens[i]))

    if checkCondition(utter, CO2Iden):
        count,tokens = checkCount(utter, CO2Iden)
        for i in range(count):
            CO2.append((stTime,utter_original,tokens[i]))
            
    


# ==========Part 3: write the result into output excel sheet==========
df0 = pd.DataFrame(AA0orAB0,columns=["StTime", "line", "token"])
df0["type"]="ain't"
df1 = pd.DataFrame(AA1,columns=["StTime", "line", "token"])
df1["type"]="AA1"
df2 = pd.DataFrame(AA2,columns=["StTime", "line", "token"])
df2["type"]="AA2"
df3 = pd.DataFrame(AB1,columns=["StTime", "line", "token"])
df3["type"]="AB1"
df4 = pd.DataFrame(CO2,columns=["StTime", "line", "token"])
df4["type"]="CO2"
data_frames = [df0, df1, df2, df3, df4]
df_merged = reduce(lambda  left,right: pd.merge(left,right,
                                            how='outer'), data_frames) # merge the dataframes from different labels
df_merged.to_csv(speakerID+".csv")   # output the csv file
    
