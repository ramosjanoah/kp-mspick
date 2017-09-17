import os.path
import pandas as pd
import math
import sys
# checking file

global temp

def checkFile():
    counter = 0
    for Quantity in range(2):
        for Price in range(2):
            for SubsFactor in range(2):
                for DaysFactor in range(2):
                    filename = "result"
                    if Price:
                        filename += "_p"
                    if Quantity:
                        filename += "_q"
                    if Price or Quantity:
                        filename += "_nonlinear"
                    filename += "_tf_sigmoid"
                    if SubsFactor:
                        filename += "_sf_2.0"
                    if DaysFactor:
                        filename += "_df_30"
                    _file = 'data/gridSearchResult/'+filename+'.csv'
                    if os.path.exists(_file):
                        print "EXIST : " + _file 
                        counter += 1
                    else:
                        print "NOT EXIST : " + _file                     
    if counter == 16:
        return True
    else:
        return False


def deleteNaN(DataFrame, parameter, value=0):
    for index, row in DataFrame.iterrows():
        if math.isnan(row[parameter]):
            DataFrame.set_value(index, 'M+', value)
            row[parameter] = value
    
def MakeOptimizeDataFrame(MinHarmonic = True):
    global temp
    mainDataFrame = pd.DataFrame()
    counter = 1
    for Quantity in range(2):
        for Price in range(2):
            for SubsFactor in range(2):
                for DaysFactor in range(2):
                    filename = "result"
                    if Price:
                        filename += "_p"
                    if Quantity:
                        filename += "_q"
                    if Price or Quantity:
                        filename += "_nonlinear"
                    filename += "_tf_sigmoid"
                    if SubsFactor:
                        filename += "_sf_2.0"
                    if not DaysFactor:
                        filename += "_df_30"
                    _file = 'data/gridSearchResult/'+filename+'.csv'
                    df = pd.read_csv(_file)
#                    print df
#                    if MinHarmonic:
#                        df = df[df.MH > 0]
                    
                    deleteNaN(df, 'M+')
                    deleteNaN(df, 'M-')
                    groups = df.groupby(by=['Category'])                    

                    for group in groups:
                        temp = group
                        #print group[1]['M+'].idxmax()
                        series = group[1].loc[group[1]['M+'].idxmax(skipna=True)]
                        mainDataFrame = mainDataFrame.append(series, ignore_index = True)                    
                    print str(counter) + ".."
                    counter += 1
                    print mainDataFrame
    return mainDataFrame

MinHarmonic = True

if len(sys.argv) > 0:
    for idx, val in enumerate(sys.argv):
        if sys.argv[idx] == '-mh':
            MinHarmonic = True
        else:
            MinHarmonic = False
        if sys.argv[idx] == '-o':
            output = sys.argv[idx+1]
        else:
            output = 'optimalSearch.py.csv'

prefix = 'data/'

if MinHarmonic:
    prefix += 'mh_'
else:
    prefix += 'nomh_'

output = prefix + output        

print "Saving to " + output + ".."

result = MakeOptimizeDataFrame(MinHarmonic)

result.to_csv(output)