#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 14:33:14 2017

@author: ramosjanoah
"""
import pandas as pd
import dengraph_lib as dg
import sys
import json
import os.path
reload(dg)

if len(sys.argv) == 1:
    print "Command:"
    print "-p : add it if the input file weight is using price"
    print "-q : add it if the input file weight is using quantity"
    print "-s : add it if the input file weight is using subs factor"
    print "-d : add it if the input file weight is using days factor"
    print "-n : add it if the input file weight is not using anything"
    print "-all : add it if you want to update everything"
    print "-nosave : add it if you dont want to save the file"
    print "-dir : add it to add directory of weight. Default = 'data/'"
#    sys.exit()

plain = False
price = False
qty = False
days = False
subs = False
nosave = False
noupdate = False
noload = False
dir_ = "data/"
_all = False

PriceGrid_str = ""
QtyGrid_str = ""
Subs_str = ""
DayGrid_str = ""
trx = "weight.csv"
suffix = ""

# hack
# price = True
# qty = True
# subs = True
# days = True
# nosave = True
# noload = True

for idx, val in enumerate(sys.argv):
    if sys.argv[idx] == '-n':
        plain = True
    if sys.argv[idx] == "-p":
        price = True
        PriceGrid_str = "_p"
    if sys.argv[idx] == "-q":
        qty = True        
        QtyGrid_str = "_q"
    if sys.argv[idx] == "-s":
        subs = True
        Subs_str = "_s"
    if sys.argv[idx] == "-d":
        days = True
        DayGrid_str = "_d"
    if sys.argv[idx] == "-dir":
        dir_ = sys.argv[idx]
    if sys.argv[idx] == "-nosave":
        nosave = True
    if sys.argv[idx] == "-noupdate":
        noupdate = True
    if sys.argv[idx] == "-noload":
        noload = True
    if sys.argv[idx] == "-all":
        _all = True


if _all:
    for qty in range(2):
        for price in range(2):
            for subs in range(2):
                for days in range(2):
                    suffix = ""
                    trx = "weight"
                    if price:
                        suffix += "_p"
                        trx += "_price"
                    if qty:
                        suffix += "_q"
                        trx += "_quantity"
                    if subs:
                        suffix += "_s"
                        trx += "_subs"
                    if days:
                        suffix += "_d"
                    if subs:
                        state_folder = "subs_" + str(2.0) + "_days_" + str(30)
                    else:
                        state_folder = "subs_" + str(1.1) + "_days_" + str(30)

                    dg.readStateData('data/' + state_folder + "/stateWriterWeight.csv")
                    dg.readMaxStateData('data/' + state_folder + "/maxStateWriterWeight.csv")      
                    
                    df_trx = pd.read_csv('data/weight/' + trx)

                    with open('data/category_id.json') as data_file:    
                        data = json.load(data_file)

                    universe = {}

                    if not noload:
                        for key, value in data.iteritems():
                            file_ = "graph/"+key+".0"+suffix
                            #print file_
                            if os.path.isfile(file_+".DenGraph"):
                                universe[float(key)] = dg.DenGraph(category=float(key))
                                universe[float(key)].Load(file_)
                        
                    if not noupdate:
                        dg.inputTransactionDataFrameToGraph(df = df_trx, sigmoid = True, world=universe, Init=False, useDaysFactor=days)

                    if not nosave:
                        for key, value in universe.iteritems():
                            filename = str(key) + ".0" + PriceGrid_str + QtyGrid_str + Subs_str + DayGrid_str
                            universe[key].Save("graph/" + filename)

else:
    if price:
        if qty:
            if subs:
                trx = "weight_price_quantity_subs.csv"
                suffix = "_p_q_s"
            else:
                trx = "weight_price_quantity.csv"
                suffix = "_p_q"
        else:
            if subs:
                trx = "weight_price_subs.csv"
                suffix = "_p_s"
            else:
                trx = "weight_price.csv"
                suffix = "_p"
    else:
        if qty:
            if subs:
                trx = "weight_quantity_subs.csv"
                suffix = "_q_s"
            else:
                trx = "weight_quantity.csv"
                suffix = "_q"
        else:
            if subs:
                trx = "weight_subs.csv"
                suffix = "_s"

    if subs:
        state_folder = "subs_" + str(2.0) + "_days_" + str(30)
    else:
        state_folder = "subs_" + str(1.1) + "_days_" + str(30)

    dg.readStateData('data/' + state_folder + "/stateWriterWeight.csv")
    dg.readMaxStateData('data/' + state_folder + "/maxStateWriterWeight.csv")

    if plain:
        trx = "weight.csv"    

    # load

    df_trx = pd.read_csv('data/weight/' + trx)

    with open('data/category_id.json') as data_file:    
        data = json.load(data_file)

    universe = {}

    if not noload:
        for key, value in data.iteritems():
            file_ = "graph/"+key+".0"+suffix
            #print file_
            if os.path.isfile(file_+".DenGraph"):
                universe[float(key)] = dg.DenGraph(category=float(key))
                universe[float(key)].Load(file_)
        
    if not noupdate:
        dg.inputTransactionDataFrameToGraph(df = df_trx, sigmoid = True, world=universe, Init=False, useDaysFactor=days)

    if not nosave:
        for key, value in universe.iteritems():
            filename = str(key) + ".0" + PriceGrid_str + QtyGrid_str + Subs_str + DayGrid_str
            universe[key].Save("graph/" + filename)

    dg.writeStateToFile('data/' + state_folder + "/stateWriterWeight.csv")
    dg.writeMaxStateToFile('data/' + state_folder + "/maxStateWriterWeight.csv")