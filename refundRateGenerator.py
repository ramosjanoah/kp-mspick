#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 14:47:28 2017

@author: raudi
"""

import pandas as pd
import json

trx = None
nodes = {}

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

def runRefundRate():
    global nodes,trx
    for index, row in trx.iterrows():
        if pd.isnull(row['stuff_category_id']):
            category = '-1.0'
        else:
            category = row['stuff_category_id']
        if (nodes.get(str(category))) == None:
            if row['state'] == "remitted":
                nodes[str(category)] = {str(row['seller_id']): {"remitted": 1, "refunded" : 0}}
            else:
                nodes[str(category)] = {str(row['seller_id']): {"remitted": 0, "refunded" : 1}}
        else:
            if (nodes[str(category)].get(str(row['seller_id'])) == None):
                if row['state'] == "remitted":
                    nodes[str(category)][str(row['seller_id'])] = {"remitted": 1, "refunded" : 0}
                else:
                    nodes[str(category)][str(row['seller_id'])] = {"remitted": 0, "refunded" : 1}
            else:
                if row['state'] == "remitted":
                    nodes[str(category)][str(row['seller_id'])]["remitted"] += 1
                else:
                    nodes[str(category)][str(row['seller_id'])]["refunded"] += 1

def loadRefundRateFromFile(filename):
    global nodes
    json_file = open(filename)
    json_str = json_file.read()
    nodes = json.loads(json_str)    
          
def saveRefundRateToFile(filename):
    global nodes
    with open(filename, 'w') as fp:
        json.dump(nodes, fp)

def updateRefundRate(priorRefundRateFile, newTransactionFile):
    global trx,nodes
    readTransactionData(newTransactionFile)
    loadRefundRateFromFile(priorRefundRateFile)
    runRefundRate()
    saveRefundRateToFile(priorRefundRateFile)
    print nodes

def buildRefundRate(refundRateFile, transactionFile):
    global trx,nodes
    readTransactionData(transactionFile)
    runRefundRate()
    saveRefundRateToFile(refundRateFile)
    print nodes

buildRefundRate('refundRate.json','data/trx.csv')
#updateRefundRate('refundRate.json','data/trx.csv')