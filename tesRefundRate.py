#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 17:59:44 2017

@author: raudi
"""

import pandas as pd
import dengraph_lib as dg
import json 
reload(dg)

json_file = open('WebApp/data/category_id.json')
json_str = json_file.read()
categories = json.loads(json_str) 

print json_str

for key in categories:
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
                    try:
                        graph = dg.DenGraph()
                        graph.Load('graph/'+str(key['id'])+'.0'+suffix)
                        graph.UpdateRefundRate('refundRate.json')
                        graph.CalculateRefundRateCluster()
                        graph.Save('graph/'+str(key['id'])+'.0'+suffix)
                        print key
                    except:
                        continue
#    print graph.Cluster
