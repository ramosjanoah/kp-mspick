#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 14:42:16 2017

@author: ramosjanoah
"""
import networkx as nx
import matplotlib as plt
import pandas as pd


subs = pd.read_csv("langganan.csv")
subs.head() 
subs = pd.DataFrame(subs)
subs_sample = subs.sample(20)
subs_sample.head()

# del g
g = nx.DiGraph()
for index, row in subs_sample.iterrows():
    g.add_node(row['subscriber_id'])
    g.add_node(row['subscribed_id'])
    g.add_edge(row['subscriber_id'], row['subscribed_id'])

degree = nx.degree(g)
    
print nx.info(g)
nx.draw_shell(g, nodelist = nx.degree(g).keys(), node_size = [v * 100 for v in nx.degree(g).values()])

# help(g.nodes)