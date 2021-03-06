"""
In this module, we explore graph networks. I will use the data provided in
the chapter but I have decided to write my own implementation of the
breadth first search algorithm. I am using networkx package to make some 
nice plots of the analyzed networks. Specifically we will try to identify 
the centrality or importance of certain nodes in our network using the
Betweeness, Eigenvector and Page rank metrics.
"""

# Perform plotting imports and networkx to create a network
import networkx as nx
from matplotlib import pyplot as plt
from collections import deque
from DS_Scratch.Ch21_Network_Analysis import eigenvector_algorithm as eva
from DS_Scratch.Ch4_Linear_Algebra import make_matrix
from operator import itemgetter

# Define a little network of users with an id, a name and a node position
# for plotting
users = [   { "id": 0, "name": "Hero",  'pos': (0,0) },
            { "id": 1, "name": "Dunn",  'pos': (1,-1) },
            { "id": 2, "name": "Sue",   'pos': (1,1) },
            { "id": 3, "name": "Chi",   'pos': (2,0) },
            { "id": 4, "name": "Thor",  'pos': (3,0) },
            { "id": 5, "name": "Clive", 'pos': (4,0) },
            { "id": 6, "name": "Hicks", 'pos': (5,1) },
            { "id": 7, "name": "Devin", 'pos': (5,-1) },
            { "id": 8, "name": "Kate",  'pos': (6,0) },
            { "id": 9, "name": "Klein", 'pos': (7,0)  }]

# define the edges between the users as friendships 
friendships = [(0,1),(0,2),(1,2),(1,3),(2,3),(3,4),(4,5),(5,6),(5,7),
               (6,8),(7,8),(8,9)]

# add the friends id to each user
for user in users:
    user["friends"] =[]

for i,j in friendships:
    users[i]["friends"].append(users[j]["id"])
    users[j]["friends"].append(users[i]["id"])

# Plot of the User-Friends Network #
####################################
# Create a graph object to plot to
G = nx.Graph()
# For each user add them to the graph object with a 'position' attribute
for user in users:
    G.add_node(user["id"],pos=user['pos'])

fig1 = plt.figure(1)
fig1.suptitle("User-Friends Network",fontsize=14, fontweight='bold')
# get the nodes and attributes dictionary
positions = nx.get_node_attributes(G,'pos')
# add the friendships as edges to the graph
G.add_edges_from(friendships)
# draw the graph placing the nodes at the positions
nx.draw(G,positions)

# Breadth First Search Algorithm #
##################################
# We want to determine the shortest path(s) between any two nodes in our
# network and then count how many paths pass through each node. This is
# "betweeness centrality" metric.

def bfs_paths(graph, start_node, end_node):
    """ computes all the paths between the start_node and end_node in the
    users graph  using breath first search algorithm """
    # create a queue and initialize it to start at the start node
    queue = [(start_node, [start_node])]
    # keep a list of the nodes we have visited
    visited = []
    
    while queue:
        # get the first node, path pair
        (node, path) = queue.pop(0)
        # get the adjacent nodes (in this case friends)
        for next in graph[node]["friends"]:
            # make sure we haven't yet visited these nodes
            if next not in visited:
                # if one of the adjacents is our end_node then we yield it.
                # Note this will yield the shortest path first but there may
                # be multiple shortest paths
                if next == end_node:
                    yield path + [next]
                else:
                    # otherwise add the adjacent node and appended path to
                    # the queue
                    queue.append((next, path + [next]))
            # update the nodes we have visited
            visited.append(node)

def shortest_paths(graph, start_node, end_node):
    """ returns the shortest paths bewtween start and end_nodes in graph """
    # get all the paths between the start and end node
    paths = list(bfs_paths(graph, start_node, end_node))
    # calculate the shortest length
    min_path_length = min([len(row) for row in paths])
    # filter for only shortest paths
    shortest_paths = [path for path in paths if len(path) <=min_path_length]
    return shortest_paths

# Calulate all Shortest Paths #
###############################
# now we are ready to calculate for each node in our network the shortest
# paths to all other nodes in the network

# add shortest path and betweeness centrality keys to users
for user in users:
    user["shortest_paths"] = []
    user['betweeness_centrality'] = 0.0

# for each start and end node call shortest_paths to get all the shortest
# paths and append to users
for start_node, _ in enumerate(users):
    for end_node, _ in enumerate(users):
        if start_node != end_node:
            users[start_node]['shortest_paths'].append(shortest_paths(users,
            start_node, end_node))

# Betweeness Centrality #
#########################
# for each pair start/end nodes 
for start_node,_ in enumerate(users):
    for end_node, _ in enumerate(users):
        if start_node < end_node:
            # get all the paths, remember the nodes start at 0
            paths = users[start_node]['shortest_paths'][end_node-1]
            # get the number of paths
            num_paths = len(paths)
            # the contibution for each id in the path should be 1/n paths
            contribution = 1/float(num_paths)
            # add the contribution to each id in each path
            for path in paths:
                for id in path:
                    if id not in [start_node, end_node]:
                        users[id]['betweeness_centrality'] += contribution

# Let the size of each node be the centrality metric, 50 is arbitrary, size
# is normally 300, what matters here is size difference between nodes
sizes = [50*user['betweeness_centrality'] for user in users]

fig2 = plt.figure(2)
fig2.suptitle("Betweeness-Centrality of User-Friends Network",fontsize=14, 
              fontweight='bold')
# get the nodes and attributes dictionary
positions = nx.get_node_attributes(G,'pos')
# add the friendships as edges to the graph
G.add_edges_from(friendships)
# draw the graph placing the nodes at the positions
nx.draw(G,positions,node_size=sizes)

# Eigenvector-Centrality #
##########################
# We will use the friendships to establish an adjacency matrix which
# represents whether there is a friendship (edge) between every pair of
# users. Thus the matrix will be square. The eigenvectors from a basis set
# for this matrix one per node in the network. The eigenvalues represent how
# many connections are arriving at that node and how well connected that
# node is to other nodes with lots of connections.

def entry_fn(i, j):
    """ returns a 1 if a friendship exist b/w i,j or j,i """
    return 1 if (i, j) in friendships or (j,i) in friendships else 0

n = len(users)
# make the adjacency matrix using entry_fn
adjacency_matrix = make_matrix(n, n, entry_fn)

# now compute the eigenvalues
eigenvalues, _ = eva.find_eigenvector(adjacency_matrix)
# scale up the eigenvalues (default node size in networkx is 300)
sizes = [1000*eigenvalue for eigenvalue in eigenvalues]

# Make a plot using the eigenvalues as the node sizes
fig3 = plt.figure(3)
fig3.suptitle("Eigenvalue-Centrality of User-Friends Network",fontsize=14, 
              fontweight='bold')
# get the nodes and attributes dictionary
positions = nx.get_node_attributes(G,'pos')
# add the friendships as edges to the graph
G.add_edges_from(friendships)
# draw the graph placing the nodes at the positions
nx.draw(G,positions,node_size=sizes)

# Directed Graphs and Page Rank Algorithm #
###########################################
# list of tuple endorsements between users in our network. They form
# directed edges
endorsements = [(0,1),(1,0),(0,2),(2,0),(1,2),
                (2,1),(1,3),(2,3),(3,4),(5,4),
                (5,6),(7,5),(6,8),(8,7),(8,9)]

# add for each user who they endorse and who endorses them
for user in users:
    # add user endorsments
    user["endorses"] = []
    # add user_endorsed_by
    user["endorsed_by"] = []

for start_node, end_node in endorsements:
    users[start_node]["endorses"].append(end_node)
    users[end_node]["endorsed_by"].append(start_node)


# Create a directed graph object to plot to
DG = nx.DiGraph()
# For each user add them to the graph object with a 'position' attribute
for user in users:
    DG.add_node(user["id"],pos=user['pos'])

fig4 = plt.figure(4)
fig4.suptitle("Endorsement Network",fontsize=14, fontweight='bold')
# get the nodes and attributes dictionary
positions = nx.get_node_attributes(DG,'pos')
# add the endorsement as directed edges to the graph
DG.add_edges_from(endorsements)
# draw the graph placing the nodes at the positions
nx.draw(DG,positions)

# find the most endorsed users
endorsements_by_id = [(user["id"], len(user["endorsed_by"])) 
                       for user in users]
# now sort them
sorted(endorsements_by_id, key=itemgetter(1))

# Page Rank Algorithm #
#######################
# In addition to looking at the number of connections between nodes to
# assess centrality we can consider who it is that is making the
# connections. Connections from nodes with lots of connections should be
# wieghted somehow more than connections from less connected nodes. In terms
# of webpages this would allow a page rank to be assigned to webpages to
# determine which ones link to another webpage.

# A simplified version of this is as follows:
# 1. There is a total of 1.0 (100%) Page rank in the network
# 2. Initially this page rank is equally distributed among the nodes
# 3. At each step a large fraction of each nodes page rank is distributed
# evenly among its outgoing links
# 4. A each step the remainder of each nodes page rank is distributed evenly
# among all the nodes

def page_rank(users, damping = 0.85, num_iters = 100):
    """ ranks users based on the number of ranked connections. A ranked
    connection is when the user recieves lots of connections from other
    users with lots of connections.  """   
    # initially distribute the page rank evenly among the nodes
    num_users = len(users)
    # make a dict keyed on user_id and value of rank
    pr = {user["id"] : 1/float(num_users) for user in users}

    # assign the small fraction of rank that each node gets each iteration
    base_pr = (1-damping) / float(num_users)

    for _ in range(num_iters):
        next_pr = { user["id"] : base_pr for user in users }
        for user in users:
            # distribute the page rank among the out going links
            links_pr = pr[user["id"]] * damping
            # for each endorsee of this user add a frac of the links_pr
            for endorsee in user['endorses']:
                next_pr[endorsee] += links_pr / len(user['endorses'])
        
        # reiterate with new page rank
        pr = next_pr
    return pr

fig5 = plt.figure(5)
fig5.suptitle("Page Rank of Endorsement Network",fontsize=14, 
              fontweight='bold')
              
# Create a directed graph object to plot to
pr_DG = nx.DiGraph()

# For each user add them to the graph object with a 'position' attribute
for user in users:
    pr_DG.add_node(user["id"],pos=user['pos'])

# get the page ranks for each user (returns a dict)
page_ranks = page_rank(users)

# scale up the sizes (default is 300)
page_rank_sizes = [10000*page_ranks[id] for id in range(len(users))]

# get the nodes and attributes dictionary
positions = nx.get_node_attributes(pr_DG,'pos')

# add the endorsement as directed edges to the graph
pr_DG.add_edges_from(endorsements)

# draw the graph placing the nodes at the positions with page ranks as node
# size
nx.draw(pr_DG,positions,node_size=page_rank_sizes)

plt.show()
