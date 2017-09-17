import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

maxDegreeCentrality = 0
maxBetweenessCentrality = 0
maxClosenessCentrality = 0
minDegreeCentrality = 99999999999
minBetweenessCentrality = 99999999999
minClosenessCentrality = 99999999999
trx = pd.DataFrame()

graph = {}
iterated = {}
if not 'subsDict' in globals():
    subsDict = {}
nodeCluster = {}
counter = {}
cluster = {}

nxGraph = {}

def buildGraph(graph,category):
    global nxGraph
    nxGraph[category] = nx.DiGraph()
    graphPerCategory = graph[category]
    for buyerId, listSellerId in graphPerCategory.iteritems():
        for sellerId, quantity in listSellerId.iteritems():
            nxGraph[category].add_edge(buyerId,sellerId,weight=quantity)    
    return

def draw(G):
    pos = nx.spring_layout(G)
    nx.draw(G,pos,with_labels=True)
    edge_labels = nx.get_edge_attributes(G,'weight')
    nx.draw_networkx_edge_labels(G, pos, labels = edge_labels)
    plt.show()
    return

def multiplyWeightToNegative(G):
    for Node in G.nodes():
        for Successor in G.successors(Node):
            G[Node][Successor]['weight'] = -G[Node][Successor]['weight']
    return

def setBetweenessCentrality(G): 
    multiplyWeightToNegative(G)
    bb = nx.betweenness_centrality(G, weight = 'weight')
    nx.set_node_attributes(G, 'betweenness', bb)
    multiplyWeightToNegative(G)
    return

def getDegreeCentralityOnNodes(G, Node):
    return G.in_degree(Node)

def setDegreeCentrality(G):
    ListOfNode = G.nodes()
    for Node in ListOfNode:
        nx.set_node_attributes(G, 'degree', {Node: getDegreeCentralityOnNodes(G, Node)})
    return

def getClosenessCentralityOnNodes(G, Node):
    ListOfPredecessor = G.predecessors(Node)
    Rate = 0
    for PredecessorNode in ListOfPredecessor:
        Rate += G[PredecessorNode][Node]['weight']  
    return Rate

def setClosenessCentrality(G):
    ListOfNode = G.nodes()
    for Node in ListOfNode:
        nx.set_node_attributes(G, 'closeness', {Node: getClosenessCentralityOnNodes(G, Node)})
    return

def setRankCentrality(G, attribute):
    rates = nx.get_node_attributes(G,attribute)    
    sorted_rates = sorted(rates.items(), key=lambda x: -x[1])    
    rank = 0 
    for rate in sorted_rates:
        nx.set_node_attributes(G, 'rank_'+attribute, {rate[0]: rank})
        rank += 1
    return 

def setThreeCentrality(G):
    setClosenessCentrality(G)
    setDegreeCentrality(G)
    setBetweenessCentrality(G)
    setRankCentrality(G, 'closeness')
    setRankCentrality(G, 'degree')
    setRankCentrality(G, 'betweenness')
    return

def setMinMaxCentrality(G):
    global maxDegreeCentrality, maxClosenessCentrality, maxBetweenessCentrality
    global minDegreeCentrality, minClosenessCentrality, minBetweenessCentrality
    ListOfNode = G.nodes()
    for Node in ListOfNode:
        if maxClosenessCentrality < G.node[Node]['closeness']:
            maxClosenessCentrality = G.node[Node]['closeness']
        if maxDegreeCentrality < G.node[Node]['degree']:
            maxDegreeCentrality = G.node[Node]['degree']
        if maxBetweenessCentrality < G.node[Node]['betweenness']:
            maxBetweenessCentrality = G.node[Node]['betweenness']
        if minClosenessCentrality > G.node[Node]['closeness']:
            minClosenessCentrality = G.node[Node]['closeness']
        if minDegreeCentrality > G.node[Node]['degree']:
            minDegreeCentrality = G.node[Node]['degree']
        if minBetweenessCentrality > G.node[Node]['betweenness']:
            minBetweenessCentrality = G.node[Node]['betweenness']
    return


def setCentrality(nxGraph):
    setThreeCentrality(nxGraph)
    SetRateOutOfNodesInGraph(nxGraph)
    setMinMaxCentrality(nxGraph)
    ListOfNode = nxGraph.nodes()
    for Node in ListOfNode:
        closeness = nxGraph.node[Node]['closeness'] - minClosenessCentrality
        betweenness = nxGraph.node[Node]['betweenness'] - minBetweenessCentrality
        degree = nxGraph.node[Node]['degree'] - minDegreeCentrality
        closenessDivider = maxClosenessCentrality - minClosenessCentrality
        if (closenessDivider == 0):
            closenessPortion = 0
        else:
            closenessPortion = closeness/closenessDivider
        betweennessDivider = maxBetweenessCentrality - minBetweenessCentrality
        if (betweennessDivider == 0):
            betweennessPortion = 0
        else:
            betweennessPortion = betweenness/betweennessDivider
        degreeDivider = maxDegreeCentrality - minDegreeCentrality
        if (degreeDivider == 0):
            degreePortion = 0
        else:
            degreePortion = degree/degreeDivider
        centrality = closenessPortion + betweennessPortion + degreePortion
        nx.set_node_attributes(nxGraph, 'centrality', {Node: centrality})
    return

def RateOutOfNodeInGraph(G, Node):
    ListOfSuccessors= G.successors(Node)
    Rate = 0
    for SuccessorNode in ListOfSuccessors:
        Rate += G[Node][SuccessorNode]['weight']
    return Rate

def SetRateOutOfNodesInGraph(G):
    ListOfNode = G.nodes()
    for Node in ListOfNode:
        nx.set_node_attributes(G, 'rate_out', {Node: RateOutOfNodeInGraph(G, Node)})
    return
        
def MaxRateOutSuccessor(G, Node):
    ListOfSuccessors = G.successors(Node)
    if len(ListOfSuccessors) == 0:
        return 0
    else:
        MaxSuccessor = ListOfSuccessors[0] 
        for SuccessorNode in ListOfSuccessors:
            if (G[Node][SuccessorNode]['weight'] > G[Node][MaxSuccessor]['weight']):
                MaxSuccessor = SuccessorNode
        return MaxSuccessor

def buildCluster(buyerId,category):
    global iterated,nodeCluster,counter,cluster,nxGraph
    if iterated.get(category,"empty") == "empty":
        iterated[category] = {}
    if nodeCluster.get(category,"empty") == "empty":
        nodeCluster[category] = {}
    if cluster.get(category,"empty") == "empty":
        cluster[category] = []
    if counter.get(category,"empty") == "empty":
        counter[category] = 0
    if (iterated[category].get(buyerId,"empty") == "empty"):
        GraphCluster = nx.DiGraph()
        GraphCluster.add_node(buyerId)
        nodeCluster[category][buyerId] = counter[category]
        cluster[category].append(GraphCluster)
        counter[category] += 1
        listOfPredecessor = nxGraph[category].predecessors(buyerId)
        for predecessor in listOfPredecessor:
            totalIn = getClosenessCentralityOnNodes(nxGraph[category], predecessor)
            totalOut = RateOutOfNodeInGraph(nxGraph[category], predecessor)
            biggestSuccessor = MaxRateOutSuccessor(nxGraph[category], predecessor)
            if (buyerId == biggestSuccessor and nxGraph[category][predecessor][buyerId]['weight'] >= (totalIn - totalOut)):
                if (iterated[category].get(predecessor) == "predecessorChecked"):
                    if (nodeCluster[category].get(predecessor) != nodeCluster[category].get(buyerId)):
                        tempGraph = cluster[category][nodeCluster[category].get(predecessor)]
                        tempNoCluster = nodeCluster[category].get(predecessor)
                        tempNodes = tempGraph.nodes()
                        for node in tempNodes:
                            nodeCluster[category][node] = nodeCluster[category].get(buyerId)
                        cluster[category][nodeCluster[category][buyerId]].add_edges_from(tempGraph.edges())
                        cluster[category][nodeCluster[category][buyerId]].add_edge(predecessor,buyerId,weight=nxGraph[category][predecessor][buyerId]['weight'])          
                        cluster[category][tempNoCluster] = None  
                    else:
                        cluster[category][nodeCluster[category][buyerId]].add_edge(predecessor,buyerId,weight=nxGraph[category][predecessor][buyerId]['weight'])          
                    iterated[category][predecessor] = 'predecessorSuccessorChecked'
                elif (iterated[category].get(predecessor,"empty") == "empty"):                    
                    cluster[category][nodeCluster[category][buyerId]].add_edge(predecessor,buyerId,weight=nxGraph[category][predecessor][buyerId]['weight'])
                    iterated[category][predecessor] = 'successorChecked'
                    nodeCluster[category][predecessor] = nodeCluster[category].get(buyerId)
                    buildCluster(predecessor,category)
        iterated[category][buyerId] = 'predecessorChecked'
    elif (iterated[category].get(buyerId) == 'successorChecked'):
        listOfPredecessor = nxGraph[category].predecessors(buyerId)
        for predecessor in listOfPredecessor:
            totalIn = getClosenessCentralityOnNodes(nxGraph[category], predecessor)
            totalOut = RateOutOfNodeInGraph(nxGraph[category], predecessor)
            biggestSuccessor = MaxRateOutSuccessor(nxGraph[category], predecessor)
            if (buyerId == biggestSuccessor and nxGraph[category][predecessor][buyerId]['weight'] >= (totalIn - totalOut)):
                if (iterated[category].get(predecessor) == "predecessorChecked"):
                    if (nodeCluster[category].get(predecessor) != nodeCluster[category].get(buyerId)):
                        tempGraph = cluster[category][nodeCluster[category].get(predecessor)]
                        tempNoCluster = nodeCluster[category].get(predecessor)
                        tempNodes = tempGraph.nodes()
                        for node in tempNodes:
                            nodeCluster[category][node] = nodeCluster[category].get(buyerId)
                        cluster[category][nodeCluster[category][buyerId]].add_edges_from(tempGraph.edges())
                        cluster[category][nodeCluster[category][buyerId]].add_edge(predecessor,buyerId,weight=nxGraph[category][predecessor][buyerId]['weight'])          
                        cluster[category][tempNoCluster] = None
                    else:
                        cluster[category][nodeCluster[category][buyerId]].add_edge(predecessor,buyerId,weight=nxGraph[category][predecessor][buyerId]['weight'])    
                    iterated[category][predecessor] = 'predecessorSuccessorChecked'
                else:
                    iterated[category][predecessor] = 'successorChecked'
                    cluster[category][nodeCluster[category][buyerId]].add_edge(predecessor,buyerId,weight=nxGraph[category][predecessor][buyerId]['weight'])
                    buildCluster(predecessor,category)
        iterated[category][buyerId] = 'predecessorSuccessorChecked'
    return

def readTransactionData():
    global graph, trx
    trx = pd.read_csv('data/trx_cleaned.csv')
    for index, row in trx.iterrows():
        if (graph.get(row['stuff_category_id'],"empty") != "empty"):
            graphPerCategory = graph[row['stuff_category_id']]
            if (graphPerCategory.get(row['buyer_id'],"empty") != "empty"):
        			graphBuyer = graphPerCategory[row['buyer_id']]
        			if (graphBuyer.get(row['seller_id'],"empty") != "empty"):
        				graphBuyer[row['seller_id']] += row['quantity']
        			else:
        				graphBuyer[row['seller_id']] = row['quantity']
        			graphPerCategory[row['buyer_id']] = graphBuyer
            else:
        			graphBuyer = {row['seller_id'] : row['quantity']}
        			graphPerCategory[row['buyer_id']] = graphBuyer
            graph[row['stuff_category_id']] = graphPerCategory
        else:
            graphBuyer = {row['seller_id'] : row['quantity']}
            graphPerCategory = {row['buyer_id'] : graphBuyer}
            graph[row['stuff_category_id']] = graphPerCategory
    return

def readSubscriptionData():
    global subscription
    subscription = pd.read_csv('data/langganan.csv')

def SetSubscriptionDictionary():
    global subscription, subsDict
    print "Importing Subscription Data to Dictionary.."
    for index, row in subscription.iterrows():
        if (index % 100000) == 0:
            print str(index) + ".."
        if (subsDict.get(row['subscribed_id'], "empty") == "empty"):
            subsDict[row['subscribed_id']] = []
        subsDict[row['subscribed_id']].append(row['subscriber_id'])

def UpdateWeightBasedOnSubscription(subsDict, category):
    global nxGraph
    for Seller in nxGraph[category].nodes():
        BuyerList = nxGraph[category].predecessors(Seller)
        if (len(BuyerList) > 0) and (subsDict.get(Seller, "empty") != "empty"):
            SubscriberList = subsDict[Seller]
            BuyerSubscriberList = list(set(BuyerList).intersection(SubscriberList))
            for BuyerSubscriber in BuyerSubscriberList:
                nxGraph[category][BuyerSubscriber][Seller]['weight'] = nxGraph[category][BuyerSubscriber][Seller]['weight']*1.5

def TransactionDataPreprocessing(DF):
    # FROM trx.csv ONLY!
    # Selecting Row
    DF = DF.query("state == 'refunded' | state == 'remitted'")
    # Selecting Column
    DF = DF[['buyer_id', 'seller_id', 'quantity', 'stuff_category_id']]

    _DF = DF.groupby(['buyer_id', 'seller_id', 'stuff_category_id']).sum()
    _DF['idx'] = _DF.index
    _DF = _DF.reset_index()
    _DF[['buyer_id', 'seller_id', 'stuff_category_id']] = _DF['idx'].apply(pd.Series)
    del _DF['idx']
    return _DF



def updateBigGraph(batch):
    global iterated,nodeCluster,counter,cluster,nxGraph
    trx = pd.read_csv('data/trx_'+str(batch)+'.csv')
    trx = TransactionDataPreprocessing(trx)
    for index, row in trx.iterrows():
        if (graph.get(row['stuff_category_id'],"empty") != "empty"):
            graphPerCategory = graph[row['stuff_category_id']]
            if (graphPerCategory.get(row['buyer_id'],"empty") != "empty"):
                graphBuyer = graphPerCategory[row['buyer_id']]
                if (graphBuyer.get(row['seller_id'],"empty") != "empty"):
                    graphBuyer[row['seller_id']] += row['quantity']                      
                    nxGraph[row['stuff_category_id']][row['buyer_id']][row['seller_id']]['weight'] += row['quantity']
                    #cluster
                    totalIn = getClosenessCentralityOnNodes(nxGraph[row['stuff_category_id']], row['buyer_id'])
                    totalOut = RateOutOfNodeInGraph(nxGraph[row['stuff_category_id']], row['buyer_id'])
                    biggestSuccessor = MaxRateOutSuccessor(nxGraph[row['stuff_category_id']], row['buyer_id'])
                    if (row['seller_id'] == biggestSuccessor and nxGraph[row['stuff_category_id']][row['buyer_id']][row['seller_id']]['weight'] >= (totalIn - totalOut)):
                        if (nodeCluster[row['stuff_category_id']].get(row['buyer_id']) != nodeCluster[row['stuff_category_id']].get(row['seller_id'])):
                            moveCluster(cluster[row['stuff_category_id']][nodeCluster[row['stuff_category_id']].get(row['buyer_id'])],cluster[row['stuff_category_id']][nodeCluster[row['stuff_category_id']].get(row['seller_id'])],row['buyer_id'],row['seller_id'],row['quantity']) 
                        else:
                            cluster[row['stuff_category_id']][nodeCluster[row['stuff_category_id']][row['seller_id']]].remove_edge(row['buyer_id'],cluster[row['stuff_category_id']][nodeCluster[row['stuff_category_id']][row['seller_id']]].successors(row['buyer_id'])[0])
                            cluster[row['stuff_category_id']][nodeCluster[row['stuff_category_id']][row['seller_id']]].add_edge(row['buyer_id'],row['seller_id'],weight=nxGraph[row['stuff_category_id']][row['buyer_id']][row['seller_id']]['weight'])          
                else:
                    graphBuyer[row['seller_id']] = row['quantity']                        
                    nxGraph[row['stuff_category_id']].add_edge(row['buyer_id'],row['seller_id'],weight=row['quantity'])
        			  # kalo seller id ga ada tapi buyer ada
                    if nodeCluster[row['stuff_category_id']].get(row['seller_id']) == None:
                        GraphCluster = nx.DiGraph()
                        GraphCluster.add_node(row['seller_id'])
                        nodeCluster[row['stuff_category_id']][row['seller_id']] = counter[row['stuff_category_id']]
                        cluster[row['stuff_category_id']].append(GraphCluster)
                        counter[row['stuff_category_id']] += 1
                        totalIn = getClosenessCentralityOnNodes(nxGraph[row['stuff_category_id']], row['buyer_id'])
                        totalOut = RateOutOfNodeInGraph(nxGraph[row['stuff_category_id']], row['buyer_id'])
                        biggestSuccessor = MaxRateOutSuccessor(nxGraph[row['stuff_category_id']], row['buyer_id'])
                        if (row['seller_id'] == biggestSuccessor and nxGraph[row['stuff_category_id']][row['buyer_id']][row['seller_id']]['weight'] >= (totalIn - totalOut)):
                            if (nodeCluster[row['stuff_category_id']].get(row['buyer_id']) != nodeCluster[row['stuff_category_id']].get(row['seller_id'])):
                                moveCluster(cluster[row['stuff_category_id']][nodeCluster[row['stuff_category_id']].get(row['buyer_id'])],cluster[row['stuff_category_id']][nodeCluster[row['stuff_category_id']].get(row['seller_id'])],row['buyer_id'],row['seller_id'],row['quantity']) 
                                removeCluster(cluster[row['stuff_category_id']][nodeCluster[row['stuff_category_id']].get(row['buyer_id'])],row['buyer_id'])
                            else:
                                cluster[row['stuff_category_id']][nodeCluster[row['stuff_category_id']][row['seller_id']]].remove_edge(row['buyer_id'],cluster[row['stuff_category_id']][nodeCluster[row['stuff_category_id']][row['seller_id']]].successors(row['buyer_id'])[0])
                                cluster[row['stuff_category_id']][nodeCluster[row['stuff_category_id']][row['seller_id']]].add_edge(row['buyer_id'],row['seller_id'],weight=nxGraph[row['stuff_category_id']][row['buyer_id']][row['seller_id']]['weight'])          
                graphPerCategory[row['buyer_id']] = graphBuyer
            else:
                graphBuyer = {row['seller_id'] : row['quantity']}
                graphPerCategory[row['buyer_id']] = graphBuyer                  
                nxGraph[row['stuff_category_id']].add_edge(row['buyer_id'],row['seller_id'],weight=row['quantity'])
                if nodeCluster[row['stuff_category_id']].get(row['seller_id']) != None:
                    cluster[row['stuff_category_id']][nodeCluster[row['seller_id']]].add_edge(row['buyer_id'],row['seller_id'],weight=row['quantity'])
                    nodeCluster[row['stuff_category_id']][row['buyer_id']] = nodeCluster[row['stuff_category_id']][row['seller_id']] 
                else: #buyer ga ada, seller ga ada
                    GraphCluster = nx.DiGraph()
                    GraphCluster.add_edge(row['buyer_id'],row['seller_id'],weight=row['quantity'])
                    nodeCluster[row['stuff_category_id']][row['seller_id']] = counter[row['stuff_category_id']]
                    nodeCluster[row['stuff_category_id']][row['buyer_id']] = counter[row['stuff_category_id']]
                    cluster[row['stuff_category_id']].append(GraphCluster)
                    counter[row['stuff_category_id']] += 1                      
            graph[row['stuff_category_id']] = graphPerCategory
        else:
            nxGraph[row['stuff_category_id']] = nx.DiGraph()
            nxGraph[row['stuff_category_id']].add_edge(row['buyer_id'],row['seller_id'],weight=row['quantity'])
            
            cluster[row['stuff_category_id']] = []
            GraphCluster = nx.DiGraph()
            GraphCluster.add_edge(row['buyer_id'],row['seller_id'],weight=row['quantity'])
            nodeCluster[row['stuff_category_id']][row['seller_id']] = counter[row['stuff_category_id']]
            nodeCluster[row['stuff_category_id']][row['buyer_id']] = counter[row['stuff_category_id']]
            cluster[row['stuff_category_id']].append(GraphCluster)
            counter[row['stuff_category_id']] += 1
            
            graphBuyer = {row['seller_id'] : row['quantity']}
            graphPerCategory = {row['buyer_id'] : graphBuyer}
            graph[row['stuff_category_id']] = graphPerCategory
    return


def moveCluster(src,dst,pred,succ,wei):
    listOfPredecessor = getAllPredecessor(src, pred)
    dst.add_edges_from(src.subgraph(listOfPredecessor).edges())
    dst.add_edge(pred,succ,weight=wei)
    
def removeCluster(src,pred):
    listOfPredecessor = getAllPredecessor(src, pred)
    for Node in L:
        src.remove_nodes(Node)
    
def getAllPredecessor(G, Node):
    L = set([])
    if len(G.predecessors(Node)) > 0:
        for PredNode in G.predecessors(Node):
            getAllPredecessorRecursive(G, PredNode, L)
    L.add(Node)
    return L

def getAllPredecessorRecursive(G, Node, L):
    L.add(Node)
    if not (set((G.predecessors(Node))).issubset(L)):
        if len(G.predecessors(Node)) > 0:
            for PredNode in G.predecessors(Node):
                getAllPredecessorRecursive(G, PredNode, L)
    return

def runBuildCluster(category):
    global nxGraph
    GC = nxGraph[category].nodes()
    for buyerId in GC:
        buildCluster(buyerId,category)
    return

def MaxCentralityNode(G):
    MaxCentral = 0
    MaxCentralNode = None
    for Nodes in G.nodes(data=True):
        if (MaxCentral < Nodes[1]['centrality']):
            MaxCentralNode = Nodes[0]
            MaxCentral = Nodes[1]['centrality']
    return (MaxCentralNode, MaxCentral)

def SDBListOfGraph(G):
    Dict = {'Supplier' : [], 'CandidateDropshipper': [], 'Buyer': []}    
    for Nodes in G.nodes(data=True):
        if (Nodes[1]['closeness'] > 0 and Nodes[1]['rate_out'] > 0 ):
            Dict['DropshipperCandidate'].append(Nodes[0])
        elif (Nodes[1]['closeness'] > 0):
            Dict['Supplier'].append(Nodes[0])
        elif (Nodes[1]['rate_out'] > 0):
            Dict['Buyer'].append(Nodes[0])
    return Dict


readTransactionData()
readSubscriptionData()
if (subsDict == {}):
    SetSubscriptionDictionary()

category = 172.0
for x in trx['stuff_category_id'].unique().tolist():
    buildGraph(graph,x)
    UpdateWeightBasedOnSubscription(subsDict,x)
    runBuildCluster(x)

# cluter = filter(None, cluster)
# Is nodeCluster still used?

summary = pd.DataFrame(columns=('cluster_id', 
                                'num_nodes', 
                                'central_node', 
                                'central_node_centrality', 
                                'num_supplier', 
                                'num_c_dropshipper', 
                                'num_buyer'))

for index, clust in enumerate(cluster.get(184.0)):
    if (clust != None):
        row = []
        setCentrality(clust)   
        CentralNode = MaxCentralityNode(clust)
        SDBList = SDBListOfGraph(clust)

        row.append(index)
        row.append(len(clust.nodes()))
        row.append(CentralNode[0])
        row.append(CentralNode[1])
        row.append(len(SDBList['Supplier']))
        row.append(len(SDBList['CandidateDropshipper']))
        row.append(len(SDBList['Buyer']))
        
        print "Cluster ID                       : " + str(row[0])
        print "Number Of Node                   : " + str(row[1])        
        print "Most-Central Node ID             : " + str(row[2])
        print "Most-Central Node Centrality     : " + str(row[3])
        print "Number of Supplier               : " + str(row[4])        
        print "Number of Candidate Dropshipper  : " + str(row[5])        
        print "Number of Buyer                  : " + str(row[6])
        # draw(clust)

        summary.loc[index] = row
        
# Longest Path (?. Is it necessary?)

nxGraph[category].nodes(data=True)
updateBigGraph(1)

