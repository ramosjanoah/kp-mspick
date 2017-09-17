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

def SaveVJson(suffix):
    global universe, price, qty, subs, days
    print "Saving for suffix '" + suffix + "'.."
    with open('data/category_id.json') as data_file:    
        data = json.load(data_file)
        for key, value in data.iteritems():
            file_ = "graph/"+str(key)+".0.0"+suffix
            #print file_
            if os.path.isfile(file_+".DenGraph"):
                universe[float(str(key))] = dg.DenGraph(category=float(str(key)))
                universe[float(str(key))].Load(file_)    
    for key, value in universe.iteritems():
        filename = str(int(key)) + ".0" + suffix
        dg.SaveGraph_NodeLinkD3(universe[key], "WebApp/data/"+filename, 'sigmoid', qty, price, 'nonlinear', days, subs)
    return

if len(sys.argv) == 1:
    print "Command:"
    print "-p : add it if the update vJson include _p"
    print "-q : add it if the update vJson include _q"
    print "-s : add it if the update vJson include _s"
    print "-d : add it if the update vJson include _d"
    print "-all : add it if the update all Json"
#    sys.exit()

plain = False
price = False
qty = False
days = False
subs = False
nosave = False
noupdate = False
noload = False
all_ = False
dir_ = "data/"

PriceGrid_str = ""
QtyGrid_str = ""
Subs_str = ""
DayGrid_str = ""
trx = "weight.csv"
suffix = ""

# hack
#all_ = False
#price = True
#qty = True
# --

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
    if sys.argv[idx] == "-all":
        all_ = True

universe = {}
        
if all_:
    for qty in range(2):
        for price in range(2):
            for subs in range(2):
                for days in range(2):
                    suffix = ""
                    if price:
                        suffix += "_p"
                    if qty:
                        suffix += "_q"
                    if subs:
                        suffix += "_s"
                    if days:
                        suffix += "_d"
                    #print suffix
                    SaveVJson(suffix)
else:
    suffix = ""
    if price:
        suffix += "_p"
    if qty:
        suffix += "_q"
    if subs:
        suffix += "_s"
    if days:
        suffix += "_d"
    print suffix
    SaveVJson(suffix)
    
print "Done."

