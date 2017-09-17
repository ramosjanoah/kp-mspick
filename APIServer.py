import json
import time
import BaseHTTPServer
import dengraph_lib as dg
import networkx as nx
import cgi
reload(dg)

HOST_NAME = ''
PORT_NUMBER = 8000

#universe = {}
#clusterRank = {}
#nodeRank = {}

def InitUniverse():
    global universe
    json_file = open('WebApp/data/category_id.json')
    json_str = json_file.read()
    categories = json.loads(json_str) 
    
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
                            graph.Load('graf/'+str(key['id'])+'.0'+suffix)
                        except:
                            continue
                        universe[str(key['id'])+suffix] = graph
                        rankCluster(str(key['id'])+suffix)
        print 'category: '+str(key['id'])
                        

def rankCluster(categorysuffix):
    global clusterRank,universe
    cluster = {}
    for key, value in universe[categorysuffix].Cluster.iteritems():
        cluster[key] = {'value':(value['remitted'] - value['refunded']), 'remittedRate':1.0-value['refundRate']}
#    print cluster
    clusterRank[categorysuffix] = sorted(cluster, key=lambda x: (cluster[x]['value'], cluster[x]['remittedRate']), reverse=True)
    for clusterID in clusterRank[categorysuffix]:
        rankNode(categorysuffix,clusterID)
#clusterRank['182_p_q_s_d']

def rankNode(categorysuffix,clusterID):
    global clusterRank,universe,nodeRank
    nodes = {}
    remitted = nx.get_node_attributes(universe[categorysuffix].Graph,'remitted')
    refunded = nx.get_node_attributes(universe[categorysuffix].Graph,'refunded')
    refundRate = nx.get_node_attributes(universe[categorysuffix].Graph,'refundRate')
    for node in universe[categorysuffix].Cluster[clusterID]['CORE']:
        if remitted.get(node) != None:
            nodes[node] = {'value':(remitted[node] - refunded[node]), 'remittedRate':1.0-refundRate[node]}
    for node in universe[categorysuffix].Cluster[clusterID]['NEIGHBOR']:
        if remitted.get(node) != None:
            nodes[node] = {'value':(remitted[node] - refunded[node]), 'remittedRate':1.0-refundRate[node]}
    if nodeRank.get(categorysuffix) == None:
        nodeRank[categorysuffix] = {}
    nodeRank[categorysuffix][clusterID] = sorted(nodes, key=lambda x: (nodes[x]['value'], nodes[x]['remittedRate']), reverse=True)
      
class RefundRateAPIServer(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(s):
        global universe
        try:
            s.send_response(200)
            s.end_headers()
            s.wfile.write("POST Only")
        except Exception as ex:
            s.send_response(500)
            s.end_headers()
            print(ex)
    
    def do_POST(self):
        global universe, clusterRank, nodeRank
        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        # Begin the response
        self.send_response(200)
        self.end_headers()
#        self.wfile.write('Client: %s\n' % str(self.client_address))
#        self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
#        self.wfile.write('Path: %s\n' % self.path)
#        self.wfile.write('Form data:\n')

        # Echo back information about what was posted in the form
        try:
            suffix = ""
            if (int(form['price'].value)):
                suffix += "_p"
            if (int(form['quantity'].value)):
                suffix += "_q"
            if (int(form['subs'].value)):
                suffix += "_s"
            if (int(form['days'].value)):
                suffix += "_d"
            categorysuffix = form['category'].value+suffix
            sellerID = form['seller'].value
            sellerClusterID = nx.get_node_attributes(universe[categorysuffix].Graph,'cluster')[int(sellerID)]
            bestCluster = []
            idx = 0
            if len(universe[categorysuffix].Cluster) == 1:
                bestCluster.append('0')
            else:
                for clusterID in clusterRank[categorysuffix]:
                    if clusterID == str(sellerClusterID):
                        continue    
                    bestCluster.append(str(clusterID))
                    idx += 1
                    if idx >= 3:
                        break
            counter = 1
            for i in range(idx):
                lengthCluster = len(nodeRank[categorysuffix][bestCluster[i]])
                for j in range(lengthCluster):
                    if nodeRank[categorysuffix][bestCluster[i]][j] == int(sellerID):
                        continue
                    self.wfile.write(str(counter)+': '+str(nodeRank[categorysuffix][bestCluster[i]][j])+'\n')
                    counter += 1
                    if counter > 3:
                        break
                if counter > 3:
                    break
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            print(ex)
        return
        
if __name__ == '__main__':
#    InitUniverse()
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), RefundRateAPIServer)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)