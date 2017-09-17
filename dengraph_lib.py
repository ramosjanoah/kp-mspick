#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 11:24:08 2017

@author: ramosjanoah
"""

import sys
import matplotlib.pyplot as plt
import networkx as nx
#from dengraph.graphs.distance_graph import DistanceGraph
#from dengraph.dengraph import DenGraphIO
import pandas as pd
from datetime import date
from datetime import datetime
import random
import math
import json
from networkx.readwrite import json_graph
import copy



DEFAULT_MAX_DISTANCE = 0.5 # development purpose
DEFAULT_MIN_NEIGHBOR = 2 # development purpose
DEFAULT_MIN_HARMONIC = 2 # development purpose

DEFAULT_GRAPH = 2 # development purpose
CONST_MAX_DISTANCE = 9999999999

SubscriptionFactor = None
NormalizationUpperLimit = None
NormalizationLowerLimit = None
DayFactorSmoothness = None
MaximumPrice = {}
MaximumQuantity = {}

SubscriptionFactorTransaction = None
NormalizationUpperLimitTransaction = None
NormalizationLowerLimitTransaction = None
DayFactorSmoothnessTransaction = None
MaximumPriceTransaction = {}
MaximumQuantityTransaction = {}

GridResultDataFrame = pd.DataFrame()

 
class DenGraph:
    Counter = 0
    def __init__(self, category = -1, MAX_DISTANCE = DEFAULT_MAX_DISTANCE, MIN_NEIGHBOR = DEFAULT_MIN_NEIGHBOR, MIN_HARMONIC = DEFAULT_MIN_HARMONIC):
        self.Category = category
        self.MAX_DISTANCE = MAX_DISTANCE
        self.MIN_NEIGHBOR = MIN_NEIGHBOR  
        self.MIN_HARMONIC = DEFAULT_MIN_HARMONIC
        self.Graph = nx.DiGraph()
        self.Cluster = {}
        self.CoreDictionary = {} 
        self.STACK_OF_NODES = []
        self.DICTIONARY_OF_NODES = {}
        self.SET_OF_NODES = []
        self.CURRENT_CLUSTER = 0
        
    def __str__(self):
        str_= ""
        str_ += "Information about Graph" + "\n"
        str_ += "DenGraph Category ID    : " + str(self.Category) + "\n"
        str_ += "Number of Node          : " + str(len(self.Graph.nodes())) + "\n"
        str_ += "Number of Edge          : " + str(len(self.Graph.edges())) + "\n"
        str_ += "Max Distance of Neighbor: " + str(self.MAX_DISTANCE) + "\n"
        str_ += "Min Number of Neighbor  : " + str(self.MIN_NEIGHBOR) + "\n"
        str_ += "Min Harmonic of Core   : " + str(self.MIN_HARMONIC) + "\n"
        str_ += "Number of Core          : " + str(len(self.CoreDictionary)) + "\n"
        str_ += "Number of Cluster       : " + str(len(self.Cluster)) + "\n"
        print "Call drawGraph function to see the Graph.\n"
        return str_
    
    def drawGraph(self, isUsingLabel=False):
        if isUsingLabel:
            pos = nx.spring_layout(self.Graph)
            nx.draw(self.Graph,pos,with_labels=True)
            edge_labels = nx.get_edge_attributes(self.Graph,'distance')
            nx.draw_networkx_edge_labels(self.Graph, pos, labels = edge_labels)
            plt.show()
        else:
            pos = nx.spring_layout(self.Graph)
            nx.draw(self.Graph,pos,with_labels=True)
            plt.show()
        return

    def getHarmonicCentralityOnNodes(self, Node):
        HarmonicDict = nx.harmonic_centrality(self.Graph, distance = 'distance')
        return HarmonicDict[Node]

    def setHarmonicCentrality(self):
        HarmonicDict = nx.harmonic_centrality(self.Graph, distance = 'distance')
        nx.set_node_attributes(self.Graph, 'harmonic', HarmonicDict)    

    def setHarmonicCentralityOfNode(self, Node):
        nx.set_node_attributes(self.Graph, 'harmonic', {Node: self.getHarmonicCentralityOnNodes(Node)})
        return
    
    def setDegreeOut(self):
        ListOfNode = self.Graph.nodes()
        for Node in ListOfNode:
            nx.set_node_attributes(self.Graph, 'degree_out', {Node: self.getDegreeOut(Node)})
        return

    def getDegreeOut(self, Node):
        ListOfSuccessors= self.Graph.successors(Node)
        Rate = 0
        for SuccessorNode in ListOfSuccessors:
            Rate += 1/self.Graph[Node][SuccessorNode]['distance']
        return Rate

    def setWeightOfGraph(self):
        # IS : There must be weight in edge
        # FS : There is distance atribute in edge, = 1/weight
        for Edge in self.Graph.edges():
            self.Graph[Edge[0]][Edge[1]]['weight'] = 1.0/(self.Graph[Edge[0]][Edge[1]]['distance'])
    
    def getDistance(self, G, node_from, node_to, distanceParameter):
        if G.has_edge(node_from, node_to):
            #print node_from + " " + node_to + " : " + str(G[node_from][node_to][distanceParameter])
            return G[node_from][node_to][distanceParameter]
        else:
            #print node_from + " " + node_to + " : inf"
            return 999
        # This is must be modified to be better, should is it use weight or something else

    def denGraphClustering(self, MaxDistance=None, MinNeighbor=None, MinHarmonic=None):
        #FS : returning list of cluster
        if MaxDistance != None:
            self.MAX_DISTANCE = MaxDistance
        
        if MinNeighbor != None:
            self.MIN_NEIGHBOR = MinNeighbor  

        if MinHarmonic != None:
            self.MIN_HARMONIC = MinHarmonic        

        self.Cluster = {}
        self.CoreDictionary = {} 
        self.STACK_OF_NODES = []
        self.setHarmonicCentrality()
        self.setDegreeOut()
        DictionaryOfCluster = {}
        
        #Make it Undirected
        G_accent = self.Graph.to_undirected()
    
        #Make DistanceGraph of the Undirected Graph
        ListOfNodes = G_accent.nodes()
        DictionaryChecked = {}
        for Nodes in self.Graph.nodes():
            DictionaryChecked[Nodes] = False
        counter = 0                
        for CurrentNode in ListOfNodes:
            counter += 1
            if DictionaryChecked[CurrentNode] == False and self.checkHarmonic(CurrentNode) and len(G_accent.neighbors(CurrentNode)) >= self.MIN_NEIGHBOR:
                #check distance
                L = []            
                for Neigh in G_accent.neighbors(CurrentNode):
                    if self.getDistance(G_accent, CurrentNode, Neigh, 'distance') <= self.MAX_DISTANCE:
                        L.append(Neigh)
                if len(L) >= self.MIN_NEIGHBOR:
                    #print "Core :) " + str(CurrentNode)
                    DictionaryOfCluster[self.CURRENT_CLUSTER] = {'CORE': [], 'NEIGHBOR': []}
                    DictionaryChecked[CurrentNode] = True
                    DictionaryOfCluster[self.CURRENT_CLUSTER]['CORE'].append(CurrentNode)
                    self.CoreDictionary[CurrentNode] = self.CURRENT_CLUSTER
                    self.STACK_OF_NODES = self.STACK_OF_NODES + L 
                    L = []
                    NeighborDict = {}
                    while self.STACK_OF_NODES != []:
                        PopNode = self.STACK_OF_NODES.pop()
                        if DictionaryChecked[PopNode] == False and self.checkHarmonic(PopNode) and len(G_accent.neighbors(PopNode)) >= self.MIN_NEIGHBOR:
                            LX = []
                            for Neigh in G_accent.neighbors(PopNode):
                                if self.getDistance(G_accent, PopNode, Neigh, 'distance') <= self.MAX_DISTANCE:
                                     LX.append(Neigh)
                            if len(LX) >= self.MIN_NEIGHBOR:
                                self.STACK_OF_NODES = self.STACK_OF_NODES + LX
                                DictionaryOfCluster[self.CURRENT_CLUSTER]['CORE'].append(PopNode)
                                self.CoreDictionary[PopNode] = self.CURRENT_CLUSTER
                                #print "Core :) " + str(PopNode)
                            else:
                                if NeighborDict.get(PopNode,'empty') == 'empty':
                                    DictionaryOfCluster[self.CURRENT_CLUSTER]['NEIGHBOR'].append(PopNode)
                                    NeighborDict[PopNode] = True
                        else:
                            if DictionaryChecked[PopNode] == False or not(self.checkHarmonic(PopNode) and len(G_accent.neighbors(PopNode)) >= self.MIN_NEIGHBOR):
                                if NeighborDict.get(PopNode,'empty') == 'empty':
                                    DictionaryOfCluster[self.CURRENT_CLUSTER]['NEIGHBOR'].append(PopNode)
                                    NeighborDict[PopNode] = True
                        DictionaryChecked[PopNode] = True
                    self.CURRENT_CLUSTER = self.CURRENT_CLUSTER + 1    
        self.Cluster = DictionaryOfCluster
        return

    def checkHarmonic(self, Node):
        if nx.get_node_attributes(self.Graph, 'harmonic')[Node] >= self.MIN_HARMONIC:
            return True
        else:
            return False
                
    def ClusterFusion(self, IDCluster1, IDCluster2):
        """ menggabungkan Cluster dengan id IDCluster1 dengan IDCluster2 """
        if IDCluster1 > IDCluster2:
            self.Cluster[IDCluster1]['CORE'].extend(self.Cluster[IDCluster2]['CORE'])
            self.Cluster[IDCluster1]['NEIGHBOR'].extend(self.Cluster[IDCluster2]['NEIGHBOR'])
            self.Cluster[IDCluster1]['NEIGHBOR'] = list(set(self.Cluster[IDCluster1]['NEIGHBOR']) - set(self.Cluster[IDCluster1]['CORE']))
            for Core in self.Cluster[IDCluster2]['CORE']:
                self.CoreDictionary[Core] = IDCluster1
            self.Cluster.pop(IDCluster2, None)
        else:
            self.Cluster[IDCluster2]['CORE'].extend(self.Cluster[IDCluster1]['CORE'])
            self.Cluster[IDCluster2]['NEIGHBOR'].extend(self.Cluster[IDCluster1]['NEIGHBOR'])
            self.Cluster[IDCluster2]['NEIGHBOR'] = list(set(self.Cluster[IDCluster2]['NEIGHBOR']) - set(self.Cluster[IDCluster2]['CORE']))
            for Core in self.Cluster[IDCluster1]['CORE']:
                self.CoreDictionary[Core] = IDCluster2
            self.Cluster.pop(IDCluster1, None)
        
    def recursiveChecking(self, Node):   
        #print "recursiveChecking(" + str(Node) + ")"
        #self.Counter += 1
        #print str(self.Counter)
        if self.isCoreQualify(Node):
            if self.CoreDictionary.get(Node,None) == None:
                if self.CURRENT_CLUSTER == None:
                    try:
                        c = int(self.Cluster.keys()[-1]) + 1
                        self.CURRENT_CLUSTER = c
                    except IndexError:
                        self.CURRENT_CLUSTER = 0
                    self.Cluster[self.CURRENT_CLUSTER] = {"CORE":[], "NEIGHBOR":[]}                
                self.Cluster[self.CURRENT_CLUSTER]["CORE"].append(Node)
                try:
                    self.Cluster[self.CURRENT_CLUSTER]["NEIGHBOR"].remove(Node)
                except ValueError:
                    pass
                    
                self.CoreDictionary[Node] = self.CURRENT_CLUSTER
                self.STACK_OF_NODES.extend(self.Graph.successors(Node))
                self.STACK_OF_NODES.extend(self.Graph.predecessors(Node)) 
                G_accent = self.Graph.to_undirected()
                while self.STACK_OF_NODES != []:
                    pop = self.STACK_OF_NODES.pop()
                    
                    if str(self.Category) == 182.0:
                        print "DER " + str(G_accent[Node][pop]['distance'])
                    if G_accent[Node][pop]['distance'] < self.MAX_DISTANCE:
#                        continue
                        pass
                        
                    self.recursiveChecking(pop)
                #self.recursiveChecking(Node)                
            elif self.CoreDictionary.get(Node,None) != self.CURRENT_CLUSTER:
                print str(self.CURRENT_CLUSTER)
                self.ClusterFusion(self.CoreDictionary[Node], self.CURRENT_CLUSTER)
        else:
            if self.CURRENT_CLUSTER != None:
                self.Cluster[self.CURRENT_CLUSTER]["NEIGHBOR"].append(Node)
    
    def isCoreQualify(self, Node):
        self.setHarmonicCentralityOfNode(Node)
        result = False
        if self.checkHarmonic(Node) and len(self.Graph.to_undirected().neighbors(Node)) >= self.MIN_NEIGHBOR:
            G_accent = self.Graph.to_undirected()
            LX = []
            for Neigh in G_accent.neighbors(Node):
                if self.getDistance(G_accent, Node, Neigh, 'distance') <= self.MAX_DISTANCE:
                    LX.append(Neigh)
            if len(LX) >= self.MIN_NEIGHBOR:
                result = True
        return result

    def UpdateEdgeWeight(self, Node1, Node2, DeltaWeight):
        self.Graph[Node1][Node2]['distance'] =+ 1/(1/self.Graph[Node1][Node2]['distance'] + DeltaWeight)
        self.setHarmonicCentralityOfNode(Node2)
                   
    def CoreNeighborOfNode(self, Node):
        result = set(self.Graph.predecessors(Node) + self.Graph.successors(Node))
        #print "R " + str(result)
        for N in Node:
            if not self.CoreDictionary.get(N, False):
                result.pop(N)
        return result
    
    def NodeAsNeighborCheck(self, Node1, Node2):
        """
        Check if Node1 is in Node2 Cluster. If not, deleted it.
        """
        try:
            self.Cluster[self.CoreDictionary[Node2]]['NEIGHBOR'].remove(Node1)    
        except ValueError:
            pass

        return
        
    def UpdateCluster_AddEdge_old(self, Node1, Node2):
        """
        IS : Antara Node 1 dan Node 2 belum ada Edge
        FS : Syarat DenGraph terpenuhi
        """        
        self.setHarmonicCentralityOfNode(Node1)        
        self.setHarmonicCentralityOfNode(Node2)

        if self.Graph[Node1][Node2]['distance'] < self.MAX_DISTANCE:            
            if Node1 in self.CoreDictionary:
                if Node2 in self.CoreDictionary:
                    if self.CoreDictionary[Node1] != self.CoreDictionary[Node2]:
                        self.ClusterFusion(self.CoreDictionary[Node1], self.CoreDictionary[Node2])
                else:
                    self.CURRENT_CLUSTER = self.CoreDictionary[Node1]
                    self.recursiveChecking(Node2)
            else:
                if Node2 in self.CoreDictionary:
                    self.CURRENT_CLUSTER = self.CoreDictionary[Node2]
                    self.recursiveChecking(Node1)
                else:
                    self.CURRENT_CLUSTER = None
                    self.recursiveChecking(Node2)

    def UpdateCluster_AddEdge(self, Node1, Node2):
        """
        IS : Antara Node 1 dan Node 2 belum ada Edge
        FS : Syarat DenGraph terpenuhi
        """        
        self.setHarmonicCentralityOfNode(Node1)        
        self.setHarmonicCentralityOfNode(Node2)

        if self.Graph[Node1][Node2]['distance'] < self.MAX_DISTANCE:            
            if Node1 in self.CoreDictionary:
                if Node2 in self.CoreDictionary:
                    if self.CoreDictionary[Node1] != self.CoreDictionary[Node2]:
                        self.ClusterFusion(self.CoreDictionary[Node1], self.CoreDictionary[Node2])
                else:
                    IDCluster1 = self.CoreDictionary[Node1]
                    self.recursiveChecking_o(Node2, IDCluster1)
            else:
                if Node2 in self.CoreDictionary:
                    IDCluster2 = self.CoreDictionary[Node2]
                    self.recursiveChecking_o(Node1, IDCluster2)
                else:
                    if self.isCoreQualify(Node2):
                        try:
                            IDCluster = int(self.Cluster.keys()[-1]) + 1
                        except IndexError:
                            IDCluster = 0
                        self.recursiveChecking_o(Node2, IDCluster)
        return 
    
    def UpdateCluster_EdgeChangePositively(self, Node1, Node2):
        """
        IS : Antara Node 1 dan Node 2 belum ada Edge
        FS : Syarat DenGraph terpenuhi
        """        
        self.setHarmonicCentralityOfNode(Node1)        
        self.setHarmonicCentralityOfNode(Node2)

        if self.Graph[Node1][Node2]['distance'] < self.MAX_DISTANCE:            
            if Node1 in self.CoreDictionary:
                if Node2 in self.CoreDictionary:
                    if self.CoreDictionary[Node1] != self.CoreDictionary[Node2]:
                        self.ClusterFusion(self.CoreDictionary[Node1], self.CoreDictionary[Node2])
                else:
                    IDCluster1 = self.CoreDictionary[Node1]
                    self.recursiveChecking_o(Node2, IDCluster1)
            else:
                if Node2 in self.CoreDictionary:
                    IDCluster2 = self.CoreDictionary[Node2]
                    self.recursiveChecking_o(Node1, IDCluster2)
                else:
                    if self.isCoreQualify(Node2):
                        try:
                            IDCluster = int(self.Cluster.keys()[-1]) + 1
                        except IndexError:
                            IDCluster = 0
                        self.recursiveChecking_o(Node2, IDCluster)
        return 


    def recursiveChecking_o(self, Node, IDCluster):   
        if self.isCoreQualify(Node):
            if self.Cluster.get(IDCluster,'empty') == 'empty':
                self.Cluster[IDCluster] = {"CORE":[], "NEIGHBOR":[]}                
            self.Cluster[IDCluster]["CORE"].append(Node)                
            try:
                self.Cluster[IDCluster]["NEIGHBOR"].remove(Node)
            except ValueError:
                pass                    
            self.CoreDictionary[Node] = IDCluster
            self.STACK_OF_NODES.extend(self.Graph.successors(Node))
            self.STACK_OF_NODES.extend(self.Graph.predecessors(Node)) 
            G_accent = self.Graph.to_undirected()

            while self.STACK_OF_NODES != []:
                pop = self.STACK_OF_NODES.pop()
                if G_accent[Node][pop]['distance'] < self.MAX_DISTANCE:                        
                    self.recursiveChecking_o(pop, IDCluster)  
        else:
            self.Cluster[IDCluster]["NEIGHBOR"].append(Node)
    
    def UpdateCluster_EdgeChangeNegatively(self, Node1, Node2):
        """ Note : Will be used if edge from node 1 to node 2 changed negatively
        """        

        if self.Graph[Node1][Node2] > self.MAX_DISTANCE:  
            if Node1 in self.CoreDictionary:
                if Node2 in self.CoreDictionary:
                    if self.CoreDictionary[Node1] == self.CoreDictionary[Node2]:
                        if self.isCoreQualify(Node1):
                            IDCluster1 = self.CoreDictionary[Node1]
                            self.DeleteCluster(IDCluster1)
                            self.recursiveChecking_o(Node1, IDCluster1)
                        if self.isCoreQualify(Node2):
                            IDCluster2 = self.CoreDictionary[Node2]
                            self.DeleteCluster(IDCluster2)
                            self.recursiveChecking_o(Node2, IDCluster2)                            
                else:
                    IDCluster1 = self.CoreDictionary[Node1]
                    self.DeleteCluster(IDCluster1)
                    if self.isCoreQualify(Node1):
                        self.recursiveChecking_o(Node1, IDCluster1)
            else:
                if Node2 in self.CoreDictionary:
                    IDCluster2 = self.CoreDictionary[Node2]
                    self.DeleteCluster(IDCluster2)
                    if self.isCoreQualify(Node2):
                        self.recursiveChecking_o(Node2, IDCluster2)
                else:
                    pass
                    """ if there's no core between the edge, there's no need to check """
                        
    def DeleteCluster(self, IDCluster):
        #try:
            dict_ = self.CoreDictionary.copy()
            self.Cluster.pop(IDCluster, None)
            for key, value in dict_.iteritems():
                if value == IDCluster:
                    self.CoreDictionary.pop(key, None)
        #except:
            #pass

    def UpdateCluster_RemoveEdge(self, Node1, Node2):
        """ Note : Will be used if edge from node 1 to node 2 is deleted
        """        
        #print "---S---"
        self.setHarmonicCentralityOfNode(Node2)
        if self.CoreDictionary.get(Node1, -1) != -1:
            if self.CoreDictionary.get(Node2, -1) != -1:
                self.RemoveCluster(Node1)
                
                self.CURRENT_CLUSTER = None
                if self.isCoreQualify(Node1):
                    self.recursiveChecking(Node1)
                else:
                    self.UpdateCluster_UncoreNode(Node1)
                    
                self.CURRENT_CLUSTER = self.Cluster.keys()[-1] + 1
#                print str(self.CURRENT_CLUSTER)
#                print str(self.CoreDictionary)

                if self.CoreDictionary.get(Node2, -1) == -1:
                    if self.isCoreQualify(Node2):
                        self.recursiveChecking(Node2)
                    else:
                        STACK_OF_CC = []
                        STACK_OF_CC.extend(self.Graph.successors(Node2))
                        STACK_OF_CC.extend(self.Graph.predecessors(Node2)) 

                        while STACK_OF_CC != []:
                            pop = STACK_OF_CC.pop()
                            print pop
                            if self.isCoreQualify(pop):
                                self.CURRENT_CLUSTER = self.Cluster.keys()[-1] + 1
                                self.Cluster[self.CURRENT_CLUSTER] = {"CORE":[], "NEIGHBOR":[]}
                                self.recursiveChecking(pop)
            else:
#                print "---2---"
                if self.CoreDictionary.get(Node1, -1) != -1:
                    # print "---3---"
                    # node 2 diilangin dari cluster node 1, kalo gapunya tetangga Core Cluster Node 1

                    if not self.isCoreQualify(Node1):
                        self.UpdateCluster_UncoreNode(Node1)
                    self.NodeAsNeighborCheck(Node2, Node1)
        else:
            if self.CoreDictionary.get(Node2, -1) != -1:
                # node 1 diilangin dari cluster node 2, kalo gapunya tetangga Core Cluster Node 2
                self.NodeAsNeighborCheck(Node1, Node2)
                if not self.isCoreQualify(Node2):                    
                    self.UpdateCluster_UncoreNode(Node2)
            else:
                #print "---4---"
                pass 
                """ do nothing"""           
    
    def RemoveCluster(self, Node):
        ResettedCluster = self.CoreDictionary.get(Node, False)            
        ResettedCore = self.Cluster[ResettedCluster]['CORE']
        
        #print ("RC : " + str(ResettedCore))
        for RC in ResettedCore:
            self.CoreDictionary.pop(RC)
        
        self.Cluster.pop(ResettedCluster)                        

     

    def UpdateCluster_UncoreNode(self, Node):
        STACK_OF_CC = []
        STACK_OF_CC.extend(self.Graph.successors(Node))
        STACK_OF_CC.extend(self.Graph.predecessors(Node)) 

        ResettedCluster = self.CoreDictionary.get(Node, False)            
        ResettedCore = self.Cluster[ResettedCluster]['CORE']
        
        #print ("RC : " + str(ResettedCore))
        for RC in ResettedCore:
            self.CoreDictionary.pop(RC)
        
        self.Cluster.pop(ResettedCluster)
    
        while STACK_OF_CC != []:
            pop = STACK_OF_CC.pop()
            #print pop
            if self.isCoreQualify(pop):
                try:
                    self.CURRENT_CLUSTER = self.Cluster.keys()[-1] + 1
                except IndexError:
                    self.CURRENT_CLUSTER = 0
                self.Cluster[self.CURRENT_CLUSTER] = {"CORE":[], "NEIGHBOR":[]}
                self.recursiveChecking(pop)
            else:
              pass  
                
        return
    
    def updatePriorWeight(self, sigmoid = False):
        global MaximumQuantity, MaximumPrice, MaximumQuantityTransaction, MaximumPriceTransaction
        global SubscriptionFactorTransaction, NormalizationUpperLimitTransaction, NormalizationLowerLimitTransaction, DayFactorSmoothnessTransaction, SubscriptionFactor, NormalizationUpperLimit, NormalizationLowerLimit, DayFactorSmoothness
        if (MaximumQuantity.get(self.Category) != MaximumQuantityTransaction.get(self.Category)) or (MaximumPrice.get(self.Category) != MaximumPriceTransaction.get(self.Category)) or (SubscriptionFactorTransaction != SubscriptionFactor) or (NormalizationUpperLimitTransaction != NormalizationUpperLimit) or (NormalizationLowerLimitTransaction != NormalizationLowerLimit) or (DayFactorSmoothnessTransaction != DayFactorSmoothness):
            for Edge in self.Graph.edges(data=True):
                quantity = 0 
                price = 0 
                subs = None
#                priorDistance = self.Graph[Edge[0]][Edge[1]]['distance']
                for key, value in Edge[2]['distribution'].iteritems():
                    currentDate = datetime.now() 
                    currentDate = currentDate.date() 
                    dateFormat = "%Y-%m-%d" 
                    transactionDate = datetime.strptime(key, dateFormat).date() 
                    daysDiff = (currentDate - transactionDate).days 
                    daysFactor = None
                    if sigmoid:
                        daysFactor = 1.0 / (1.0 + math.exp(daysDiff / (-1 * DayFactorSmoothnessTransaction)))
                    else: #reluh
                        daysFactor = (DayFactorSmoothnessTransaction - daysDiff)/DayFactorSmoothnessTransaction
                        if daysFactor < 0:
                            daysFactor = 0
                    for transactionInDay in Edge[2]['distribution'][key]:
                        transactionInDay['quantity'] = self.calculateNewNormalizeValue(transactionInDay['quantity'],MaximumQuantity,MaximumQuantityTransaction,NormalizationUpperLimit,NormalizationUpperLimitTransaction,NormalizationLowerLimit,NormalizationLowerLimitTransaction)
                        transactionInDay['price'] = self.calculateNewNormalizeValue(transactionInDay['quantity'],MaximumQuantity,MaximumQuantityTransaction,NormalizationUpperLimit,NormalizationUpperLimitTransaction,NormalizationLowerLimit,NormalizationLowerLimitTransaction)                        
                        quantity += transactionInDay['quantity']
                        price += transactionInDay['price']
                        subs = transactionInDay['subs']
                self.Graph[Edge[0]][Edge[1]]['distance'] = 1/(quantity*price*daysFactor)
                if int(subs):
                    self.Graph[Edge[0]][Edge[1]]['distance'] *= SubscriptionFactor
                    self.Graph[Edge[0]][Edge[1]]['distance'] /= SubscriptionFactorTransaction
#                if priorDistance < value.Graph[Edge[0]][Edge[1]]['distance']:
#                    self.UpdateCluster_EdgeChangePositively(Edge[0], Edge[1])
#                elif priorDistance > value.Graph[Edge[0]][Edge[1]]['distance']:
#                    self.UpdateCluster_EdgeChangeNegatively(Edge[0], Edge[1])


    def updatePriorWeight_old(self, sigmoid = False):
        global MaximumQuantity, MaximumPrice, MaximumQuantityTransaction, MaximumPriceTransaction
        global SubscriptionFactorTransaction, NormalizationUpperLimitTransaction, NormalizationLowerLimitTransaction, DayFactorSmoothnessTransaction, SubscriptionFactor, NormalizationUpperLimit, NormalizationLowerLimit, DayFactorSmoothness
        if (MaximumQuantity.get(self.Category) != MaximumQuantityTransaction.get(self.Category)) or (MaximumPrice.get(self.Category) != MaximumPriceTransaction.get(self.Category)) or (SubscriptionFactorTransaction != SubscriptionFactor) or (NormalizationUpperLimitTransaction != NormalizationUpperLimit) or (NormalizationLowerLimitTransaction != NormalizationLowerLimit) or (DayFactorSmoothnessTransaction != DayFactorSmoothness):
            for Edge in self.Graph.edges(data=True):
                quantity = 0 
                price = 0 
                subs = None
                priorDistance = self.Graph[Edge[0]][Edge[1]]['distance']
                for key, value in Edge[2]['distribution'].iteritems():
                    currentDate = datetime.now() 
                    currentDate = currentDate.date() 
                    dateFormat = "%Y-%m-%d" 
                    transactionDate = datetime.strptime(key, dateFormat).date() 
                    daysDiff = (currentDate - transactionDate).days 
                    daysFactor = None
                    if sigmoid:
                        daysFactor = 1.0 / (1.0 + math.exp(daysDiff / (-1 * DayFactorSmoothnessTransaction)))
                    else: #reluh
                        daysFactor = (DayFactorSmoothnessTransaction - daysDiff)/DayFactorSmoothnessTransaction
                        if daysFactor < 0:
                            daysFactor = 0
                    Edge[2]['distribution'][key]['quantity'] = self.calculateNewNormalizeValue(value['quantity'],MaximumQuantity,MaximumQuantityTransaction,NormalizationUpperLimit,NormalizationUpperLimitTransaction,NormalizationLowerLimit,NormalizationLowerLimitTransaction)
                    Edge[2]['distribution'][key]['price'] = self.calculateNewNormalizeValue(value['price'],MaximumPrice,MaximumPriceTransaction,NormalizationUpperLimit,NormalizationUpperLimitTransaction,NormalizationLowerLimit,NormalizationLowerLimitTransaction)
                    quantity += Edge[2]['distribution'][key]['quantity']
                    price += Edge[2]['distribution'][key]['price']
                    subs = Edge[2]['distribution'][key]['subs']
                self.Graph[Edge[0]][Edge[1]]['distance'] = 1/(quantity*price*daysFactor)
                if int(subs):
                    self.Graph[Edge[0]][Edge[1]]['distance'] *= SubscriptionFactor
                    self.Graph[Edge[0]][Edge[1]]['distance'] /= SubscriptionFactorTransaction
                if priorDistance < value.Graph[Edge[0]][Edge[1]]['distance']:
                    self.UpdateCluster_EdgeChangePositively(Edge[0], Edge[1])
                elif priorDistance > value.Graph[Edge[0]][Edge[1]]['distance']:
                    self.UpdateCluster_EdgeChangeNegatively(Edge[0], Edge[1])

    def SaveGPickle(self, filename):
        nx.write_gpickle(self.Graph,filename)
        return
    
    def LoadGPickle(self, filename):
        self.Graph = nx.read_gpickle(filename)
        return
        
    def SaveGraph_NodeLink(self, filename):
        data = json_graph.node_link_data(self.Graph)
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)
        return
    
    def LoadGraph_NodeLink(self, filename):
        with open(filename) as data_file:    
            data = json.load(data_file)
        self.Graph = json_graph.node_link_graph(data, directed = True)
        return 
    
    def Save(self, filename):
        graph_filename = filename + ".Graph"
        filename += ".DenGraph"
        data = {'Category' : self.Category,
                'MAX_DISTANCE' : self.MAX_DISTANCE,
                'MIN_NEIGHBOR' : self.MIN_NEIGHBOR, 
                'MIN_HARMONIC' : self.MIN_HARMONIC, 
                'Graph_filename' : graph_filename, 
                'Cluster' : self.Cluster, 
                'CoreDictionary' : self.CoreDictionary}
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)
        self.SaveGraph_NodeLink(graph_filename)
        
        return
    
    def Load(self, filename):
        filename += ".DenGraph"
        with open(filename) as json_data:
            Loaded = json.load(json_data)
        self.Graph = None
        self.LoadGraph_NodeLink(Loaded['Graph_filename'])
        self.Category = Loaded['Category']
        self.MAX_DISTANCE = Loaded['MAX_DISTANCE']
        self.MIN_NEIGHBOR = Loaded['MIN_NEIGHBOR']
        self.MIN_HARMONIC = Loaded['MIN_HARMONIC']
        self.Cluster = Loaded['Cluster']
        self.CoreDictionary = Loaded['CoreDictionary']
        return        

    def ClusterGraph(self, ClusterID):
        result = list(self.Cluster[ClusterID]['CORE'])
        result.extend(self.Cluster[ClusterID]['NEIGHBOR'])
        Graph = self.Graph.subgraph(result)
        return Graph
    
    def GraphGridSearch(self, MinHarmonicList = [0, 1, 10],
                        MaxDistanceList = [0.4, 0.8, 1, 1.5],
                        MinNeighborList = [1, 2, 4],
                        result = None):
        
        global GridResultDataFrame, universe
        if result != None:
            GridResultDataFrame = result
        CList = []
        MHList = []
        MDList = []
        MNList = []
        MPlusList = []
        MNegList = []
        MNegDistanceList = []

        DenGraph_accent = copy.deepcopy(self)
        for MH in MinHarmonicList:
            for MD in MaxDistanceList:
                for MN in MinNeighborList:
                    DenGraph_accent.denGraphClustering(MinHarmonic = MH, MaxDistance = MD, MinNeighbor = MN)
                    CPL = DenGraph_accent.ClusteringQuality_CPL()                        
                    #print CPL
                    CList.append(self.Category)
                    MHList.append(MH)
                    MDList.append(MD)
                    MNList.append(MN)
                    MPlusList.append(CPL[0])
                    MNegList.append(CPL[1])
                    MNegDistanceList.append(CPL[2])
                    
        df = pd.DataFrame({'Category' : CList, 'MH' : MHList, 'MD': MDList, 'MN': MNList, 'M+': MPlusList, 'M-': MNegList, 'M-D':MNegDistanceList})
        return df

    def ClusteringQuality_CPL(self, printProcess = False):

        self.setWeightOfGraph()

        if printProcess:
            print "MH = " + str(self.MIN_HARMONIC)
            print "MD = " + str(self.MAX_DISTANCE)
            print "MN = " + str(self.MIN_NEIGHBOR)
            print "C  = " + str(len(self.Cluster))
            
        if (len(self.Cluster )== 0):
            return (0,0,0)

        # M_Positive
        if printProcess:
            SumOfCPL = 0.0
            for key, value in self.Cluster.iteritems():
                ClusterGraph = self.ClusterGraph(key)
                avg = nx.average_shortest_path_length(ClusterGraph.to_undirected(), weight = 'distance')
                print str(avg)
                SumOfCPL += 1.0/avg
        else :
            SumOfCPL = 0.0
            for key, value in self.Cluster.iteritems():
                ClusterGraph = self.ClusterGraph(key)
                avg = nx.average_shortest_path_length(ClusterGraph.to_undirected(), weight = 'distance')

                SumOfCPL += 1.0/avg     
                
        M_Positive = SumOfCPL/len(self.Cluster)
    
        if (len(self.Cluster )== 1):
            return (M_Positive,0,0)
        # M_Negative 
        G_accent = self.Graph.to_undirected()
        M_Negative = 0.0
        M_NegativeDistance = 0.0
        for clusterID_I, valueI in self.Cluster.iteritems():
            for clusterID_J, valueJ in self.Cluster.iteritems(): 
                if (clusterID_I != clusterID_J):
                    #print "checking Cluster "  + str(clusterID_I) + " : " + str(clusterID_J)
                    ListNodesI = list(self.Cluster[clusterID_I]['CORE'])
                    ListNodesI.extend(self.Cluster[clusterID_I]['NEIGHBOR'])  
                    ListNodesJ = list(self.Cluster[clusterID_J]['CORE'])
                    ListNodesJ.extend(self.Cluster[clusterID_J]['NEIGHBOR'])  
                    
                    Counter = 0.0
                    CounterDistance = 0.0
                    
                    for NodesI in ListNodesI:
                        for NodesJ in ListNodesJ:
                            if G_accent.has_edge(NodesI, NodesJ):
                               Counter += 1
                               CounterDistance += G_accent[NodesI][NodesJ]['distance']
                    
                    EdgePenalty = Counter / (len(ListNodesI) * len(ListNodesJ))
                    EdgePenaltyDistance = CounterDistance / (len(ListNodesI) * len(ListNodesJ))
                    
                    M_Negative =+ EdgePenalty
                    M_NegativeDistance =+ EdgePenaltyDistance
        
        M_Negative = M_Negative * 2 / (len(self.Cluster) * (len(self.Cluster)-1))
        M_NegativeDistance = M_NegativeDistance * 2 / (len(self.Cluster) * (len(self.Cluster)-1))
    
        return (M_Positive, M_Negative, M_NegativeDistance)    

    # CPL reference : https://hal.archives-ouvertes.fr/inria-00542690/document
    
    def UpdateRefundRate(self, refundRateFile):
        json_file = open(refundRateFile)
        json_str = json_file.read()
        nodes = json.loads(json_str) 
        remitted = {}
        refunded = {}
        refundRate = {}
        for nodeId, value in nodes[str(self.Category)].iteritems():
            remitted[int(nodeId)] = value['remitted']
            refunded[int(nodeId)] = value['refunded']
            refundRate[int(nodeId)] = float(value['refunded'])/(float(value['remitted'])+float(value['refunded']))
#        print remitted
#        print refunded
#        print refundRate
        nx.set_node_attributes(self.Graph, 'remitted', remitted)
        nx.set_node_attributes(self.Graph, 'refunded', refunded)
        nx.set_node_attributes(self.Graph, 'refundRate', refundRate)
        
    def CalculateRefundRateCluster(self):
        for key, value in self.Cluster.iteritems():
            remitted = 0
            refunded = 0
            graphRemitted = nx.get_node_attributes(self.Graph, 'remitted')
            graphRefunded = nx.get_node_attributes(self.Graph, 'refunded')
            for node in value['CORE']:
                if graphRemitted.get(node) != None:
                    remitted += graphRemitted[node]
                    refunded += graphRefunded[node]
            for node in value['NEIGHBOR']:
                if graphRemitted.get(node) != None:
                    remitted += graphRemitted[node]
                    refunded += graphRefunded[node]
            self.Cluster[key]['remitted'] = remitted
            self.Cluster[key]['refunded'] = refunded
            self.Cluster[key]['refundRate'] = float(refunded)/(float(remitted)+float(refunded))
    
    
#--------------------- end of class ---------------------#

def inputTransactionDataFrameToGraph(df, world = None,  Init=True, Clustering=False, sigmoid=False, printProcess=False, useDaysFactor=True, DayFactorSmoothnessTransaction = 2):
    global universe
    if world != None:
        universe = world
    counter = 0
    counter_1 = 0
    total_rows = df.shape[0]
    if printProcess:
        print "Total row = " + str(total_rows) + ". Reading Data..."
        print "Init : " + str(Init)
    if Init == True:
        if printProcess:
            print "Initiate Universe..."
        for index, row in df.iterrows():
            if universe.get(row['category']) == None:
                universe[row['category']] = DenGraph(row['category'], DEFAULT_MAX_DISTANCE, DEFAULT_MIN_NEIGHBOR, DEFAULT_MIN_HARMONIC)
                counter_1 += 1
            
            if not universe[row['category']].Graph.has_edge(row['buyer_id'], row['seller_id']):
                universe[row['category']].Graph.add_edge(row['buyer_id'], row['seller_id'], distribution = {row['date'] : [{'quantity': row['quantity'], 'price' : row['price'], 'subs' :row['subs']}]})
            else:
                if universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution'].get(row['date']) == None:
                    universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution'][row['date']] = [{'quantity': row['quantity'], 'price' : row['price'], 'subs' : row['subs']}]
                else:
                    universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution'][row['date']].append({'quantity': row['quantity'], 'price' : row['price'], 'subs' :row['subs']})
            counter += 1
        if printProcess:
            print "Reading Data Done. "
            print "Total row = " + str(counter) + "."
            print "Total category = " + str(counter_1) + "."
            
            print "Updating Edge Attributes..."
        
        counter = 0
        for key, value in universe.iteritems():
            #print "Update Graph. Category : " + str(key)
            for Edge in value.Graph.edges(data=True):
                weight = 0
                for key2, value2 in Edge[2]['distribution'].iteritems():
                    if useDaysFactor:
                        currentDate = datetime.now() 
                        currentDate = currentDate.date()
                        dateFormat = "%Y-%m-%d" 
                        transactionDate = datetime.strptime(key2, dateFormat).date() 
                        daysDiff = (currentDate - transactionDate).days - 2
                        daysFactor = None
                        if sigmoid:
                            daysFactor = 1.0 / (1.0 + math.exp(daysDiff / (-1 * DayFactorSmoothnessTransaction)))
                        else: #reluh
                            daysFactor = (DayFactorSmoothnessTransaction - daysDiff)/DayFactorSmoothnessTransaction
                            if daysFactor < 0:
                                daysFactor = 0
                    else:
                        daysFactor = 1
                    
                    for transactionInDay in Edge[2]['distribution'][key2]:
                        weightTemp = transactionInDay['quantity']*transactionInDay['price']*daysFactor

                    if int(value2[0]['subs']):
                        weightTemp *= SubscriptionFactorTransaction
                    weight += weightTemp
                try:
                    value.Graph[Edge[0]][Edge[1]]['distance'] = float(1)/weight
                except ZeroDivisionError:
                    value.Graph[Edge[0]][Edge[1]]['distance'] = CONST_MAX_DISTANCE
                    
            if Clustering:
                value.denGraphClustering()
    else:
        if printProcess:
            print "Update Universe..."
        for index, row in df.iterrows():
            #print "Row Transaction : " + str(index)
            #print "Category Transaction : " + str(row['category'])
            isNew = False
            if universe.get(row['category']) == None:
                universe[row['category']] =  DenGraph(row['category'], DEFAULT_MAX_DISTANCE, DEFAULT_MIN_NEIGHBOR, DEFAULT_MIN_HARMONIC)                
                counter_1 += 1
            
            if not universe[row['category']].Graph.has_edge(row['buyer_id'], row['seller_id']):
                universe[row['category']].Graph.add_edge(row['buyer_id'], row['seller_id'], distribution = {row['date'] : [{'quantity': row['quantity'], 'price' : row['price'], 'subs' :row['subs']}]})
                isNew = True
            else:
                if universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution'] == None:
                    universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution'] = {}
                    universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution'][row['date']] = [{'quantity': row['quantity'], 'price' : row['price'], 'subs' :row['subs']}]
                    continue
                
                if universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution'].get(row['date']) == None:
                    universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution'][row['date']] = [{'quantity': row['quantity'], 'price' : row['price'], 'subs' :row['subs']}]
                else:
                    universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution'][row['date']].append({'quantity': row['quantity'], 'price' : row['price'], 'subs' :row['subs']})
            weight = 0
            if not isNew:
                priorDistance = universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distance']
            #print "AAAAA " + str(len(universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution']))
            #print universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution']
            for key2, value2 in universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distribution'].iteritems():
                #print "BBBB"
                if useDaysFactor:
                    currentDate = datetime.now()
                    currentDate = currentDate.date()
                    dateFormat = "%Y-%m-%d" 
                    transactionDate = datetime.strptime(key2, dateFormat).date() 
                    daysDiff = (currentDate - transactionDate).days 
                    daysFactor = None
                    if sigmoid:
                        daysFactor = 1.0 / (1.0 + math.exp(daysDiff / (-1 * DayFactorSmoothnessTransaction)))
                    else: #reluh
                        daysFactor = (DayFactorSmoothnessTransaction - daysDiff)/DayFactorSmoothnessTransaction
                        if daysFactor < 0:
                            daysFactor = 0
                else:
                    daysFactor = 1

                for element in value2:
                    try:
                        weightTemp = element['quantity']*element['price']*daysFactor
                    except:
                        print value2
                        print element
                    if int(element['subs']):
                        weightTemp *= SubscriptionFactorTransaction
                weight += weightTemp
            universe[row['category']].Graph[row['buyer_id']][row['seller_id']]['distance'] = 1/weight
            counter += 1
            if isNew:
                universe[row['category']].UpdateCluster_AddEdge(row['buyer_id'], row['seller_id'])
            else:
                #print "priorDistance : " + str(priorDistance)
                #print "Distance : " + str(1/weight)
                if priorDistance < 1/weight:
                    #print "InputTransaction : UpdateCluster_EdgeChangePositively"
                    universe[row['category']].UpdateCluster_EdgeChangePositively(row['buyer_id'], row['seller_id'])
                elif priorDistance > 1/weight:
                    #print "InputTransaction : UpdateCluster_EdgeChangeNegatively"
                    universe[row['category']].UpdateCluster_EdgeChangeNegatively(row['buyer_id'], row['seller_id'])                

            if counter % 5000 == 0:
                print str((counter*100/total_rows)) + "% row.."
        
        if printProcess:
            print "Reading Data Done. "
            print "Total row = " + str(counter) + "."
            print "Total category = " + str(counter_1) + "."
            
    print "inputTransactionDataFrameToGraph Done."
    return

def randomDate():
    start_date = date.today().replace(day=1, month=1).toordinal()
    end_date = date.today().toordinal()
    random_day = date.fromordinal(random.randint(start_date, end_date))
    return random_day

def writeMaxStateToFile(filename):
    global MaximumQuantity, MaximumPrice, MaximumQuantityTransaction, MaximumPriceTransaction
    global universe
    for key, value in universe.iteritems():
        #print 'CEK ',MaximumQuantity[key], MaximumPrice[key], MaximumQuantityTransaction[key], MaximumPriceTransaction[key]
        if (pd.isnull(MaximumQuantity[key])) and (MaximumQuantityTransaction[key] != None):
            MaximumQuantity[key] = MaximumQuantityTransaction[key]
        elif (MaximumQuantity[key] != None) and (MaximumQuantityTransaction[key] != None):
            MaximumQuantity[key] = max(MaximumQuantity[key],MaximumQuantityTransaction[key])
        if (pd.isnull(MaximumPrice[key])) and (MaximumPriceTransaction[key] != None):
            MaximumPrice[key] = MaximumPriceTransaction[key]
        elif (MaximumPrice[key] != None) and (MaximumPriceTransaction[key] != None):
            MaximumPrice[key] = max(MaximumPrice[key],MaximumPriceTransaction[key])
        #print 'AFTER CEK ',MaximumQuantity[key], MaximumPrice[key], MaximumQuantityTransaction[key], MaximumPriceTransaction[key]
    dfg = pd.DataFrame(columns=('category', 'maxQuantityGraph', 'maxPriceGraph'))
    counter = 0
    print "Writing max graph state to ", filename
    for key, value in MaximumQuantity.iteritems():
        dfg.loc[counter] = [key, value, MaximumPrice[key]]
        counter += 1
    df = pd.DataFrame(columns=('category', 'maxQuantity', 'maxPrice'))
    counter = 0
    print "Writing max state to ", filename
    for key, value in MaximumQuantityTransaction.iteritems():
        df.loc[counter] = [key, value, MaximumPriceTransaction[key]]
        counter += 1
    result = pd.merge(dfg, df, how='outer', on=['category'])
    result.to_csv(filename)
    print "Writing max state to ", filename, " has been succeed."
    
def writeStateToFile(filename):
    global SubscriptionFactorTransaction, NormalizationUpperLimitTransaction, NormalizationLowerLimitTransaction, DayFactorSmoothnessTransaction, SubscriptionFactor, NormalizationUpperLimit, NormalizationLowerLimit, DayFactorSmoothness
    print "Writing state to ", filename
    df = pd.DataFrame(columns=('graphSubscriptionFactor', 'graphNormalizationUpperLimit', 'graphNormalizationLowerLimit', 'graphDayFactorSmoothness', 'subscriptionFactor', 'normalizationUpperLimit', 'normalizationLowerLimit', 'dayFactorSmoothness'))
    df.loc[0] = [SubscriptionFactorTransaction, NormalizationUpperLimitTransaction, NormalizationLowerLimitTransaction, DayFactorSmoothnessTransaction, SubscriptionFactorTransaction, NormalizationUpperLimitTransaction, NormalizationLowerLimitTransaction, DayFactorSmoothnessTransaction]
    df.to_csv(filename)
    print "Writing state to ", filename, " has been succeed."

def readStateData(filename):
    global SubscriptionFactorTransaction, NormalizationUpperLimitTransaction, NormalizationLowerLimitTransaction, DayFactorSmoothnessTransaction, SubscriptionFactor, NormalizationUpperLimit, NormalizationLowerLimit, DayFactorSmoothness
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
                SubscriptionFactorTransaction = row['subscriptionFactor']
                NormalizationUpperLimitTransaction = row['normalizationUpperLimit']
                NormalizationLowerLimitTransaction = row['normalizationLowerLimit']
                DayFactorSmoothnessTransaction = row['dayFactorSmoothness']
                SubscriptionFactor = row['graphSubscriptionFactor']
                NormalizationUpperLimit = row['graphNormalizationUpperLimit']
                NormalizationLowerLimit = row['graphNormalizationLowerLimit']
                DayFactorSmoothness = row['graphDayFactorSmoothness']
        except:
            print "Update error"
        else:
            print "Update finish .."
    return

def readMaxStateData(filename):
    global MaximumQuantity, MaximumPrice, MaximumQuantityTransaction, MaximumPriceTransaction
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
                if (MaximumQuantityTransaction.get(row['category']) == None) or (MaximumQuantityTransaction[row['category']] < row['maxQuantity']):
                    MaximumQuantityTransaction[row['category']] = row['maxQuantity']
                if (MaximumPriceTransaction.get(row['category']) == None) or (MaximumPriceTransaction[row['category']] < row['maxPrice']):
                    MaximumPriceTransaction[row['category']] = row['maxPrice']
                if (MaximumQuantity.get(row['category']) == None) or (MaximumQuantity[row['category']] < row['maxQuantityGraph']):
                    MaximumQuantity[row['category']] = row['maxQuantityGraph']
                if (MaximumPrice.get(row['category']) == None) or (MaximumPrice[row['category']] < row['maxPriceGraph']):
                    MaximumPrice[row['category']] = row['maxPriceGraph']
        except:
            print "Update error"
        else:
            print "Update finish .."
    return

def calculateNormalizeValue(value, maxValue, scaleMax, scaleMin):
    valueParameter = float(value) / maxValue * 400.0 + 100.0
    normalizeValue = (1.0 - 100.0 / valueParameter) * 5.0 / 4.0 * (scaleMax-scaleMin) + scaleMin
    return normalizeValue

def calculateValueFromNormalize(normalizeValue, maxValue, scaleMax, scaleMin):
    value = ((500.0*(scaleMax-scaleMin))/(-4.0*normalizeValue+5.0*scaleMax-scaleMin) - 100.0)*maxValue/400.0
    return value

def calculateNewNormalizeValue(normalizeValue,oldMaxValue,newMaxValue,oldScaleMax,newScaleMax,oldScaleMin,newScaleMin):
    value = calculateValueFromNormalize(normalizeValue,oldMaxValue,oldScaleMax,oldScaleMin)
    newNormalizeValue = calculateNormalizeValue(value,newMaxValue,newScaleMax,newScaleMin)
    return newNormalizeValue


def drawGraph(Graph, isUsingLabel=False):
    if isUsingLabel:
        pos = nx.spring_layout(Graph)
        nx.draw(Graph,pos,with_labels=True)
        edge_labels = nx.get_edge_attributes(Graph,'distance')
        nx.draw_networkx_edge_labels(Graph, pos, labels = edge_labels)
        plt.show()
    else:
        pos = nx.spring_layout(Graph)
        nx.draw(Graph,pos,with_labels=True)
        plt.show()
    return

def SaveGraph_NodeLinkD3(DenGraph, filename, TimeFunction, Qty, Price, QPF, DayGrid, SubsGrid):
    harmonic = nx.get_node_attributes(DenGraph.Graph, 'harmonic')
    if len(DenGraph.CoreDictionary) > 0:
        for key, value in DenGraph.Cluster.iteritems():
            list_ = list(value['CORE'])
            list_.extend(value['NEIGHBOR'])
            for element in list_:
                nx.set_node_attributes(DenGraph.Graph, 'cluster', {element: key})
    # for element in DenGraph.Graph.nodes():
    #     if len(DenGraph.Graph.predecessors(element)) != 0:
    #         nx.set_node_attributes(DenGraph.Graph, 'harmonic', {element: (harmonic[element]/len(DenGraph.Graph.predecessors(element)))})
    #     else:
    #         nx.set_node_attributes(DenGraph.Graph, 'harmonic_average', {element: 0})
    data = json_graph.node_link_data(DenGraph.Graph)
    for link in data['links']:
        link['source'] = data['nodes'][link['source']]['id']
        link['target'] = data['nodes'][link['target']]['id']
    data['Cluster'] = DenGraph.Cluster
    data['CoreDictionary'] = DenGraph.CoreDictionary
    data['MH'] = DenGraph.MIN_HARMONIC
    data['MD'] = DenGraph.MAX_DISTANCE
    data['MN'] = DenGraph.MIN_NEIGHBOR
    data['TF'] = TimeFunction 
    data['P'] = Price
    data['Q'] = Qty
    data['DF'] = DayGrid
    data['SF'] = SubsGrid
    data['QPF'] = QPF
    with open(filename + ".d3.json", 'w') as outfile:
        json.dump(data, outfile)
    return data

global universe 
universe = {}
