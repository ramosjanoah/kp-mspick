#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 11:24:08 2017

@author: ramosjanoah
"""

import dengraph_lib as dg
import sys
import pandas as pd

### ---- GRID SEARCH ------------------------------------

universe = {}

GridResultDataFrame = pd.DataFrame()

MinHarmonicList = [2, 5]
MaxDistanceList = [0.2, 0.5, 0.8, 1.5]
MinNeighborList = [2, 4, 6]

#trx_file = ""

#default
TimeFunction = 'sigmoid'
QtyGrid = False
PriceGrid = False
QtyPriceFunction = 'nonlinear'
DayGrid = 30 # kurang 240
SubsFactorGrid = 1.1
usingSubs = False

for idx, val in enumerate(sys.argv):
    if sys.argv[idx] == '-tf':
        TimeFunction = sys.argv[idx+1]
    if sys.argv[idx] == '-q':
        QtyGrid = True
    if sys.argv[idx] == '-p':
        PriceGrid = True
    if sys.argv[idx] == '-qpf':
        if sys.argv[idx+1] == 'linear':
            pass
        elif sys.argv[idx+1] == 'nonlinear':
            QtyPriceFunction = 'nonlinear'
    if sys.argv[idx] == '-df':
        DayGrid = int(sys.argv[idx+1])
    if sys.argv[idx] == '-sf':
        usingSubs = True
        SubsFactorGrid = 2.0
    if sys.argv[idx] == '-o':
        output = sys.argv[idx+1]

if QtyGrid:
    if PriceGrid:
        if QtyPriceFunction == 'linear':
            if usingSubs != False:
                trx_file = 'weight_price_quantity_linear_subs'
            else:
                trx_file = 'weight_price_quantity_linear'
        else:
            if usingSubs != False:
                trx_file = 'weight_price_quantity_subs'
            else:
                trx_file = 'weight_price_quantity'                
    else:
        if QtyPriceFunction == 'linear':
            if usingSubs != False:
                trx_file = 'weight_quantity_linear_subs'
            else:
                trx_file = 'weight_quantity_linear'
        else:
            if usingSubs != False:
                trx_file = 'weight_quantity_subs'
            else:
                trx_file = 'weight_quantity'            
else:
    if PriceGrid:
        if QtyPriceFunction == 'linear':
            if usingSubs != False:
                trx_file = 'weight_price_linear_subs'
            else:
                trx_file = 'weight_price_linear'
        else:
            if usingSubs != False:
                trx_file = 'weight_price_subs'
            else:
                trx_file = 'weight_price'                
    else:
        if usingSubs != False:
            trx_file = 'weight_subs'
        else:
            trx_file = 'weight'  

# Filename
#DayGrid = 120
#SubsFactorGrid = 1.8

#trx_file = "weight_price_linear_subs.csv"
#state_folder = "subs_1.6_days_120"

trx_file += ".csv"
state_folder = "subs_" + str(SubsFactorGrid) + "_days_" + str(DayGrid)

print "trx_file : " + str(trx_file)
print "state_folder : " + str(state_folder)

# Read File
trx = pd.read_csv('data/weight/' + trx_file) 
print trx
dg.readStateData('data/' + str(state_folder) + "/stateWriterWeight.csv")
dg.readMaxStateData('data/' + str(state_folder) + "/maxStateWriterWeight.csv")


# Input Transaction
if (TimeFunction != 'sigmoid'):
    print "inputTransactionDataFrameToGraph(sigmoid = False)"
    dg.inputTransactionDataFrameToGraph(trx, world = universe, useDaysFactor = False)
else:
    print "inputTransactionDataFrameToGraph(sigmoid = True)"
    dg.inputTransactionDataFrameToGraph(trx, world = universe, sigmoid = True, useDaysFactor = False)


# -- Grid Search

Counter = 0
for key, value in universe.iteritems():
    GridResultDataFrame = GridResultDataFrame.append(value.GraphGridSearch(MinHarmonicList = MinHarmonicList, MaxDistanceList = MaxDistanceList, MinNeighborList = MinNeighborList))
    Counter += 1
    if Counter % 100 == 0:
        print str(Counter) + ".."


GridResultDataFrame['TimeFunction'] = TimeFunction
GridResultDataFrame['QtyGrid'] = str(QtyGrid)
GridResultDataFrame['PriceGrid'] = str(PriceGrid)
GridResultDataFrame['QtyPriceFunction'] = str(QtyPriceFunction)
GridResultDataFrame['DayGrid'] = "NotUseDaysFactor"
GridResultDataFrame['SubsFactor'] = SubsFactorGrid

print GridResultDataFrame

GridResultDataFrame.to_csv("data/gridSearchResult/" + output)

print "Data frame has been exported to : " + str(output)