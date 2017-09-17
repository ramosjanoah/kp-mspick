#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 14:41:36 2017

@author: raudi
"""

from datetime import datetime
import pandas as pd
import math
import sys

weightDictionary = {}
subsDict = {}
subsFactor = 1.2
subscriptionData = None

maxQuantity = {}
maxPrice = {}
maxQuantityGraph = {}
maxPriceGraph = {}
trx = None
scaleMin = 1
scaleMax = 10
smoothness = 30
priceFactor = False
quantityFactor = False
dateFormat = "%Y-%m-%d %H:%M:%S"
linear = False
sigmoid = False

graphSubsFactor = None
graphScaleMax = None
graphScaleMin = None
graphSmoothness = None

def readTransactionData(filename):
    global trx
    print "Reading ",filename," .."
    try:
        trx = pd.read_csv(filename)
        trx = trx[trx['state'].str.contains('remitted|refunded')]
    except:
        print "File not found or not compatible"
    else:
        print "Finish reading transaction data"
    return

def readSubscriptionData(filename):
    global subscriptionData
    print "Reading subscription data .."
    try:
        subscriptionData = pd.read_csv(filename)
    except:
        print "File not found or not compatible"
    else:
        print "Finish reading subscription data"
    return

def readStateData(filename):
    global subsFactor, scaleMax, scaleMin, smoothness, graphSubsFactor, graphScaleMax, graphScaleMin, graphSmoothness
    print "Reading state data .."
    try:
        stateData = pd.read_csv(filename)
    except:
        print "File not found or not compatible"
    else:
        print "Finish reading subscription data"
        try:
            print "Updating state .. "
            for index, row in stateData.iterrows():
                subsFactor = row['subscriptionFactor']
                scaleMax = row['normalizationUpperLimit']
                scaleMin = row['normalizationLowerLimit']
                smoothness = row['dayFactorSmoothness']
                graphSubsFactor = row['graphSubscriptionFactor']
                graphScaleMax = row['graphNormalizationUpperLimit']
                graphScaleMin = row['graphNormalizationLowerLimit']
                graphSmoothness = row['graphDayFactorSmoothness']
        except:
            print "Update error"
        else:
            print "Update finish .."
    return

def readMaxStateData(filename):
    global maxQuantity, maxPrice, maxQuantityGraph, maxPriceGraph
    print "Reading max state data .."
    try:
        maxStateData = pd.read_csv(filename)
    except:
        print "File not found or not compatible"
    else:
        print "Finish reading subscription data"
        try:
            print "Updating max state .. "
            for index, row in maxStateData.iterrows():
                if (maxQuantity.get(row['category']) == None) or (maxQuantity[row['category']] < row['maxQuantity']):
                    maxQuantity[row['category']] = row['maxQuantity']
                if (maxPrice.get(row['category']) == None) or (maxPrice[row['category']] < row['maxPrice']):
                    maxPrice[row['category']] = row['maxPrice']
                if (maxQuantityGraph.get(row['category']) == None) or (maxQuantityGraph[row['category']] < row['maxQuantityGraph']):
                    maxQuantityGraph[row['category']] = row['maxQuantityGraph']
                if (maxPriceGraph.get(row['category']) == None) or (maxPriceGraph[row['category']] < row['maxPriceGraph']):
                    maxPriceGraph[row['category']] = row['maxPriceGraph']
        except:
            print "Update error"
        else:
            print "Update finish .."
    return
        
def subscriptionDataToDictionary():
    global subsDict, subscriptionData
    print "Importing Subscription Data to Dictionary.."
    count = 0
    try:
        for index, row in subscriptionData.iterrows():
            if (index % 100000) == 0:
                print str(index) + " records.."
            if (subsDict.get(row['subscribed_id'], "empty") == "empty"):
                subsDict[row['subscribed_id']] = {}
            subsDict[row['subscribed_id']][row['subscriber_id']] = row['created_at']
            count += 1
    except:
        print "Import process has been failed, try checking the column format!"
    else:
        print "Subscription data has been added to dictionary successfully. Total records : ", count
    return

def setMaxPriceAndQuantity():
    global trx, maxQuantity, maxPrice
    priorMaxQuantity = maxQuantity
    priorMaxPrice = maxPrice
    for index, row in trx.iterrows():     
        if pd.isnull(row['stuff_category_id']):
            row['stuff_category_id'] = -1
        if maxQuantity.get(row['stuff_category_id']) == None:
            maxQuantity[row['stuff_category_id']] = float(row['quantity'])
        if maxPrice.get(row['stuff_category_id']) == None:
            maxPrice[row['stuff_category_id']] = float(row['stuff_price'])
        if maxQuantity[row['stuff_category_id']] < row['quantity']:
            maxQuantity[row['stuff_category_id']] = float(row['quantity'])
        if maxPrice[row['stuff_category_id']] < row['stuff_price']:
            maxPrice[row['stuff_category_id']] = float(row['stuff_price'])
        if (maxQuantityGraph.get(row['stuff_category_id']) != None) and (maxQuantity[row['stuff_category_id']] < maxQuantityGraph[row['stuff_category_id']]):
            maxQuantity[row['stuff_category_id']] = maxQuantityGraph[row['stuff_category_id']]
        if (maxPriceGraph.get(row['stuff_category_id']) != None) and (maxPrice[row['stuff_category_id']] < maxPriceGraph[row['stuff_category_id']]):
            maxPrice[row['stuff_category_id']] = maxPriceGraph[row['stuff_category_id']]
    print "maxQuantity has been updated from ", priorMaxQuantity," to ", maxQuantity
    print "maxPrice has been updated from ", priorMaxPrice," to ", maxPrice
    return

# for Quantity and Price using 1-100/x graph
def calculateNormalizeValue(value, maxValue, scaleMax, scaleMin, linear):
    if linear:
        normalizeValue = float(value) / maxValue * (scaleMax-scaleMin) + scaleMin
    else:
        valueParameter = float(value) / maxValue * 400.0 + 100.0
        normalizeValue = (1.0 - 100.0 / valueParameter) * 5.0 / 4.0 * (scaleMax-scaleMin) + scaleMin
    return normalizeValue

def calculateValueFromNormalize(normalizeValue, maxValue, scaleMax, scaleMin, linear):
    if linear:
        value = (normalizeValue - scaleMin) * maxValue / (scaleMax-scaleMin)
    else:
        value = ((500.0*(scaleMax-scaleMin))/(-4.0*normalizeValue+5.0*scaleMax-scaleMin) - 100.0)*maxValue/400.0
    return value

def calculateNewNormalizeValue(normalizeValue,oldMaxValue,newMaxValue,oldScaleMax,newScaleMax,oldScaleMin,newScaleMin,linear):
    value = calculateValueFromNormalize(normalizeValue,oldMaxValue,oldScaleMax,oldScaleMin,linear)
    newNormalizeValue = calculateNormalizeValue(value,newMaxValue,newScaleMax,newScaleMin,linear)
    return newNormalizeValue

def addRecordToWeightDictionary(row,quantity,price,subs,transactionDate):
    global weightDictionary
    if weightDictionary.get(row['stuff_category_id']) == None:
        weightDictionary[row['stuff_category_id']] = {}
        weightDictionary[row['stuff_category_id']][row['buyer_id']] = {}
        weightDictionary[row['stuff_category_id']][row['buyer_id']][row['seller_id']] = {}
        weightDictionary[row['stuff_category_id']][row['buyer_id']][row['seller_id']][transactionDate] = [{'quantity': quantity, 'price' : price, 'subs' :subs}]
    else:
        if weightDictionary.get(row['stuff_category_id']).get(row['buyer_id']) == None:
            weightDictionary[row['stuff_category_id']][row['buyer_id']] = {}
            weightDictionary[row['stuff_category_id']][row['buyer_id']][row['seller_id']] = {}
            weightDictionary[row['stuff_category_id']][row['buyer_id']][row['seller_id']][transactionDate] = [{'quantity': quantity, 'price' : price, 'subs' :subs}]
        else:
            if weightDictionary.get(row['stuff_category_id']).get(row['buyer_id']).get(row['seller_id']) == None:
                weightDictionary[row['stuff_category_id']][row['buyer_id']][row['seller_id']] = {}
                weightDictionary[row['stuff_category_id']][row['buyer_id']][row['seller_id']][transactionDate] = [{'quantity': quantity, 'price' : price, 'subs' :subs}]
            else:
                if weightDictionary.get(row['stuff_category_id']).get(row['buyer_id']).get(row['seller_id']).get(transactionDate) == None:
                    weightDictionary[row['stuff_category_id']][row['buyer_id']][row['seller_id']][transactionDate] = [{'quantity': quantity, 'price' : price, 'subs' :subs}]
                else:
                    weightDictionary[row['stuff_category_id']][row['buyer_id']][row['seller_id']][transactionDate].append({'quantity': quantity, 'price' : price, 'subs' :subs})


# smoothness means how fast its weight degrade, bigger value means smoother 
def calculateDaysFactor(currentDate,transactionDate,sigmoid):
    global smoothness
    daysDiff = (currentDate - transactionDate).days
    if sigmoid:
        daysFactor = 1.0 / (1.0 + math.exp(daysDiff / (-1 * smoothness)))
    else: #reluh
        daysFactor = (smoothness - daysDiff)/smoothness
        if daysFactor < 0:
            daysFactor = 0
    return daysFactor

def calculateWeight(buyer,seller,quantity,price,transactionDate):
    global subsDict, subsFactor, dateFormat
    weight = quantity * price
    if subsDict.get(seller) != None:
        if subsDict.get(seller).get(buyer) != None:
            subsDate = datetime.strptime(subsDict.get(seller).get(buyer), dateFormat).date()
            if subsDate <= transactionDate:
                weight *= subsFactor
    return weight

def transactionDataToWeightDictionary():
    global trx, weightDictionary, subsDict, maxQuantity, maxPrice, subsFactor, dateFormat,scaleMax,scaleMin,linear
    for index, row in trx.iterrows():
        if pd.isnull(row['stuff_category_id']):
            row['stuff_category_id'] = -1
        transactionDate = datetime.strptime(row['paid_at'], dateFormat).date()
        if quantityFactor:
            quantity = calculateNormalizeValue(row['quantity'],maxQuantity[row['stuff_category_id']],scaleMax,scaleMin,linear)
        else:
            quantity = 1
        if priceFactor:
            price = calculateNormalizeValue(row['stuff_price'],maxPrice[row['stuff_category_id']],scaleMax,scaleMin,linear)
        else:
            price = 1
        subs = 0
        if subsDict.get(row['seller_id']) != None:
            if subsDict.get(row['seller_id']).get(row['buyer_id']) != None:
                subsDate = datetime.strptime(subsDict.get(row['seller_id']).get(row['buyer_id']), dateFormat).date()
                if subsDate <= transactionDate:
                    subs = 1
        addRecordToWeightDictionary(row,quantity,price,subs,transactionDate)
    return
    
def writeWeightToFile(filename):
    global weighDictionary
    df = pd.DataFrame(columns=('category', 'buyer_id', 'seller_id', 'date', 'quantity', 'price', 'subs'))
    counter = 0
    print "Writing weight dictionary to ", filename
    for key1, value1 in weightDictionary.iteritems():
        for key2, value2 in value1.iteritems():
            for key3, value3 in value2.iteritems():
                for key4, value4 in value3.iteritems():
                    for i in value4:
                        df.loc[counter] = [key1, key2, key3, key4, i['quantity'], i['price'], i['subs']]
                        counter += 1
                        if (counter % 10000) == 0:
                            print str(counter) + " records.."
    print "Writing weight records to ", filename, " has been succeed. Total records : ", counter
    df.to_csv(filename)
    return

def writeMaxStateToFile(filename):
    global maxQuantity, maxPrice, maxQuantityGraph, maxPriceGraph
    dfg = pd.DataFrame(columns=('category', 'maxQuantityGraph', 'maxPriceGraph'))
    counter = 0
    print "Writing max state to ", filename
    for key, value in maxQuantityGraph.iteritems():
        dfg.loc[counter] = [key, value, maxPriceGraph[key]]
        counter += 1
    df = pd.DataFrame(columns=('category', 'maxQuantity', 'maxPrice'))
    counter = 0
    print "Writing max state to ", filename
    for key, value in maxQuantity.iteritems():
        df.loc[counter] = [key, value, maxPrice[key]]
        counter += 1
    result = pd.merge(dfg, df, how='outer', on=['category'])
    result.to_csv(filename)
    print "Writing max state to ", filename, " has been succeed."
    
def writeStateToFile(filename):
    global subsFactor, scaleMax, scaleMin, smoothness, graphSubsFactor, graphScaleMax, graphScaleMin, graphSmoothness
    print "Writing state to ", filename
    df = pd.DataFrame(columns=('graphSubscriptionFactor', 'graphNormalizationUpperLimit', 'graphNormalizationLowerLimit', 'graphDayFactorSmoothness', 'subscriptionFactor', 'normalizationUpperLimit', 'normalizationLowerLimit', 'dayFactorSmoothness'))
    df.loc[0] = [graphSubsFactor, graphScaleMax, graphScaleMin, graphSmoothness, subsFactor, scaleMax, scaleMin, smoothness]
    df.to_csv(filename)
    print "Writing state to ", filename, " has been succeed."
    
if len(sys.argv) < 3:
    print "Please type :"
    print "readWeight.py <transaction input data>.csv <weight output data>.csv [commands]"
    print "You can also use another additional command, type -h for help"
else:   
    try:
        commands = sys.argv[3:]
        errorCommand = '-h'
        if '-h' in commands and commands.index('-h') != None:
            print "-p : for adding price as parameter of weight calculation, default just using amount of transaction"
            print "-q : for adding quantity as parameter of weight calculation, default just using amount of transaction"
            print "-s [input subscription data] : for adding subscription as parameter of weight calculation, default just using amount of transaction"
            print "-sf [subscription factor] : set subscription factor's value, default 1.2"
            print "-mq [maximum quantity] : set maximum quantity on previous graph, default None"
            print "-mp [maximum price] : set maximum price on previous graph, default None"
            print "-nul [normalization's upper limit] : set normalization's upper limit, default 10"
            print "-nll [normalization's lower limit] : set normalization's lower limit, default 1"
            print "-dfs [day factor smoothness] : set day factor smoothness, default 30"
            print "-l : for using linear function for normalization, default 1/x function"
            print "-sg : for using sigmoid function for days factor, default relu function"
            print "-rs : reading state file for updating the weight calculation state, all command above will be replaced"
            print "-rms reading max state file for updating the weight calculation max state"
            sys.exit()
        errorCommand = '-p'
        if '-p' in commands and commands.index('-p') != None:
            priceFactor = True
            print "Price has been set as weight parameter successfully"
        errorCommand = '-q'
        if '-q' in commands and commands.index('-q') != None:
            quantityFactor = True
            print "Quantity has been set as weight parameter successfully"
        errorCommand = '-sf'
        if '-sf' in commands and commands.index('-sf') != None:
            subsFactor = commands[commands.index('-sf')+1]
            if subsFactor < 1.0:
                print "Subscription factor must be >= 1.0"
                sys.exit()
            else:
                print "Subscription factor has been set to :", subsFactor
        errorCommand = '-s'
        if '-s' in commands and commands.index('-s') != None:
            readSubscriptionData(commands[commands.index('-s')+1])
            subscriptionDataToDictionary()
        else:
            subsFactor = 1.0
            print "Because calculation is not using subscription factor, subscription factor has been set to :", subsFactor
        errorCommand = '-l'
        if '-l' in commands and commands.index('-l') != None:
            linear = True
            print "Linear has been set as weight parameter successfully"
        errorCommand = '-sg'
        if '-sg' in commands and commands.index('-sg') != None:
            sigmoid = True
            print "Sigmoid has been set as weight parameter successfully"
#        errorCommand = '-mq'
#        if '-mq' in commands and commands.index('-mq') != None:
#            maxQuantity = float(commands[commands.index('-mq')+1])
#            if maxQuantity < 0.0:
#                print "Maximum quantity must be >= 0.0"
#                sys.exit()
#            else:
#                print "Maximum quantity has been set to :", maxQuantity
#        errorCommand = '-mp'
#        if '-mp' in commands and commands.index('-mp') != None:
#            maxPrice = float(commands[commands.index('-mp')+1])
#            if maxPrice < 0.0:
#                print "Maximum price must be >= 0.0"
#                sys.exit()
#            else:
#                print "Maximum price has been set to :", maxPrice
        errorCommand = '-nul'
        if '-nul' in commands and commands.index('-nul') != None:
            errorCommand = '-nll'
            if '-nll' in commands and commands.index('-nll') != None:
                scaleMin = float(commands[commands.index('-nll')+1])
                errorCommand = '-nul'
                scaleMax = float(commands[commands.index('-nul')+1])
                if scaleMax <= scaleMin:
                    print "Normalization's upper limit must be bigger than lower limit !"
                    sys.exit()
                else:
                    print "Normalization's upper limit has been set to :", scaleMax
                    print "Normalization's lower limit has been set to :", scaleMin
            else:
                print "Normalization's upper limit and lower limit must be specified !"
                sys.exit()
        elif '-nll' in commands and commands.index('-nll') != None:
            errorCommand = '-nul'
            if '-nul' in commands and commands.index('-nul') != None:
                scaleMax = float(commands[commands.index('-nul')+1])
                errorCommand = '-nll'
                scaleMin = float(commands[commands.index('-nll')+1])
                if scaleMax <= scaleMin:
                    print "Normalization's upper limit must be bigger than lower limit !"
                    sys.exit()
                else:
                    print "Normalization's upper limit has been set to :", scaleMax
                    print "Normalization's lower limit has been set to :", scaleMin
            else:
                print "Normalization's upper limit and lower limit must be specified !"
                sys.exit()
        errorCommand = '-dfs'
        if '-dfs' in commands and commands.index('-dfs') != None:
            smoothness = float(commands[commands.index('-dfs')+1])
            if smoothness < 0.0:
                print "Day factor smoothness must be >= 0.0"
                sys.exit()
            else:
                print "Day factor smoothness has been set to :", smoothness
        errorCommand = '-rs'
        if '-rs' in commands and commands.index('-rs') != None:
            readStateData('data/stateWriterWeight.csv')
        errorCommand = '-rms'
        if '-rms' in commands and commands.index('-rms') != None:
            readMaxStateData('data/maxStateWriterWeight.csv')
    except:
        print "Error in command near", errorCommand
    else:
        readTransactionData(sys.argv[1])
        setMaxPriceAndQuantity()
        transactionDataToWeightDictionary()
        writeWeightToFile(sys.argv[2])
#        writeStateToFile('data/stateWriterWeight.csv')
#        writeMaxStateToFile('data/maxStateWriterWeight.csv')

#gridSubs = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
#for x in gridSubs:
#    print "python readWeight.py data/trx.csv data/weight_"+str(x)+".csv -s data/langganan.csv"+" -sf "+str(x)
#    print "python readWeight.py data/trx.csv data/weight_price_linear_"+str(x)+".csv -s data/langganan.csv"+" -sf "+str(x)+" -l -p"
#    print "python readWeight.py data/trx.csv data/weight_quantity_linear_"+str(x)+".csv -s data/langganan.csv"+" -sf "+str(x)+" -l -q"
#    print "python readWeight.py data/trx.csv data/weight_price_quantity_linear_"+str(x)+".csv -s data/langganan.csv"+" -sf "+str(x)+" -l -q -p"
#    print "python readWeight.py data/trx.csv data/weight.csv"
#    print "python readWeight.py data/trx.csv data/weight_price_linear.csv -l -p"
#    print "python readWeight.py data/trx.csv data/weight_quantity_linear.csv -l -q"
#    print "python readWeight.py data/trx.csv data/weight_price_quantity_linear.csv -l -q -p"

x = 1.1
#
print "python readWeight.py data/trx.csv data/weight_subs.csv -s data/langganan.csv"+" -sf "+str(x)
print "python readWeight.py data/trx.csv data/weight_price_linear_subs.csv -s data/langganan.csv"+" -sf "+str(x)+" -l -p"
print "python readWeight.py data/trx.csv data/weight_quantity_linear_subs.csv -s data/langganan.csv"+" -sf "+str(x)+" -l -q"
print "python readWeight.py data/trx.csv data/weight_price_quantity_linear_subs.csv -s data/langganan.csv"+" -sf "+str(x)+" -l -q -p"
print "python readWeight.py data/trx.csv data/weight.csv"
print "python readWeight.py data/trx.csv data/weight_price_linear.csv -l -p"
print "python readWeight.py data/trx.csv data/weight_quantity_linear.csv -l -q"
print "python readWeight.py data/trx.csv data/weight_price_quantity_linear.csv -l -q -p"

print "python readWeight.py data/trx.csv data/weight_price_subs.csv -s data/langganan.csv"+" -sf "+str(x)+" -p"
print "python readWeight.py data/trx.csv data/weight_quantity_subs.csv -s data/langganan.csv"+" -sf "+str(x)+" -q"
print "python readWeight.py data/trx.csv data/weight_price_quantity_subs.csv -s data/langganan.csv"+" -sf "+str(x)+" -q -p"
print "python readWeight.py data/trx.csv data/weight_price.csv -p"
print "python readWeight.py data/trx.csv data/weight_quantity.csv -q"
print "python readWeight.py data/trx.csv data/weight_price_quantity.csv -q -p"