#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 14:30:40 2017

@author: raudi
"""

import os

gridSubs = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
smoothness = [7,30,60,90,120,150,180,210,270,300,330,360]
for x in gridSubs:
    for y in smoothness:
        dir = "data/subs_"+str(x)+"_days_"+str(y)
        filename = "data/subs_"+str(x)+"_days_"+str(y)+"/stateWriterWeight.csv"
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        print "Writing state to ", filename
        df = pd.DataFrame(columns=('graphSubscriptionFactor', 'graphNormalizationUpperLimit', 'graphNormalizationLowerLimit', 'graphDayFactorSmoothness', 'subscriptionFactor', 'normalizationUpperLimit', 'normalizationLowerLimit', 'dayFactorSmoothness'))
        df.loc[0] = [None, None, None, None, x, 10, 1, y]
        df.to_csv(filename)
        print "Writing state to ", filename, " has been succeed."
        