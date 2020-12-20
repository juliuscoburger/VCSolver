import itertools

def read_edges(edges):
    vertices = {}
    nodes = 0
    edges = sorted([sorted(i) for i in edges])
    edges = list(s for s,_ in itertools.groupby(edges))
    for l in edges:
        if l[0] in vertices:
            vertices[l[0]]["neighbors"].append(l[1])
            vertices[l[0]]["active_degree"] += 1
        else:
            vertices[l[0]] = {"neighbors": [l[1]], "active_degree": 1, "active": True}
            nodes += 1
        if l[1] in vertices:
            vertices[l[1]]["neighbors"].append(l[0])
            vertices[l[1]]["active_degree"] += 1
        else:
            vertices[l[1]] = {"neighbors": [l[0]], "active_degree": 1, "active": True}
            nodes += 1
    G = {}
    G["vertices"] = vertices
    G["active_nodes"] = nodes
    G["num_edges"] = len(edges)
    G["DS"] = {}  #only active nodes in DS
    for v in G["vertices"]:
        deg = G["vertices"][v]["active_degree"]
        if deg in G["DS"]:
            G["DS"][deg].append(v)
        else:
            G["DS"][deg] = [v]

    return G

def read_input(path):
    E = []
    for l in path:
        if '#' not in l:
            s = l.strip().split(' ')
            E += [s]
    return read_edges(E)

def read_input_edges(path):
    E = []
    for l in path:
        if '#' not in l:
            s = l.strip().split(' ')
            x = [int(i) for i in s]
            E += [x]
    return E

def delete_vertices(G, v_list):
    for v in v_list:
        if G["vertices"][v]["active"]:
            G["DS"][G["vertices"][v]["active_degree"]].remove(v)
            G["active_nodes"] -= 1
            G["vertices"][v]["active"] = False
            for n in G["vertices"][v]["neighbors"]:
                G["vertices"][n]["active_degree"] -= 1 
                if G["vertices"][n]["active"]:
                    G["num_edges"] -= 1
                    deg = G["vertices"][n]["active_degree"]
                    G["DS"][deg+1].remove(n)
                    if deg in G["DS"]:
                        G["DS"][deg].append(n)
                    else: 
                        G["DS"][deg] = [n]
    return


def add_to_graph(G, v_list):
    for v in v_list:
        if not G["vertices"][v]["active"]:
            G["active_nodes"] += 1
            deg = G["vertices"][v]["active_degree"]
            if deg in G["DS"]:
                G["DS"][deg].append(v)
            else: 
                G["DS"][deg] = [v]
            G["vertices"][v]["active"] = True
            for n in G["vertices"][v]["neighbors"]:
                G["vertices"][n]["active_degree"] += 1 
                if G["vertices"][n]["active"]:
                    G["num_edges"] += 1
                    deg = G["vertices"][n]["active_degree"]
                    G["DS"][deg-1].remove(n)
                    if deg in G["DS"]:
                        G["DS"][deg].append(n)
                    else: 
                        G["DS"][deg] = [n]

    return


def get_active_neighbors(G, v):
    neighbors = G["vertices"][v]["neighbors"]
    n = []
    for nei in neighbors:
        if G["vertices"][nei]["active"]:
            n.append(nei)
    return n


def activeVertices(G):
    v_list = []
    for v in G["vertices"]:
        if G["vertices"][v]["active"]:
            v_list.append(v)
    return v_list


def DESTROY(G, v_list):
    for v in v_list:
        was_active = False
        if G["vertices"][v]["active"]:
            G["DS"][G["vertices"][v]["active_degree"]].remove(v)
            G["active_nodes"] -= 1
            was_active = True
        neighbors = G["vertices"].pop(v)
        for n in neighbors["neighbors"]:
            G["vertices"][n]["neighbors"].remove(v)
            if G["vertices"][n]["active"] and was_active:
                G["num_edges"] -= 1
                G["vertices"][n]["active_degree"] -= 1
                deg = G["vertices"][n]["active_degree"]
                G["DS"][deg+1].remove(n)
                if deg in G["DS"]:
                    G["DS"][deg].append(n)
                else: 
                    G["DS"][deg] = [n]
    return

def addVertex(G, v, neighbors):
    v_new = 'S' + v 
    G["vertices"][v_new] = {"neighbors": neighbors, "active_degree": len(neighbors), "active": True}
    G["num_edges"] += len(neighbors)
    G["active_nodes"] += 1
    deg = len(neighbors)
    if deg in G["DS"]:
        G["DS"][deg].append(v_new)
    else: 
        G["DS"][deg] = [v_new]   
    for n in neighbors:
        G["vertices"][n]["neighbors"].append(v_new)
        G["vertices"][n]["active_degree"] += 1 
        deg = G["vertices"][n]["active_degree"] 
        G["DS"][deg-1].remove(n)
        if deg in G["DS"]:
            G["DS"][deg].append(n)
        else: 
            G["DS"][deg] = [n]
    return v_new

def merge(G, v, n1, n2):
    neigh1 = get_active_neighbors(G, n1)
    neigh2 = get_active_neighbors(G, n2)
    neighbors = list(set(neigh1 + neigh2))
    v_new = addVertex(G, v, neighbors)
    delete_vertices(G, [v]+[n1]+[n2])
    return v_new

def reset(G, merge_dict):
    #keys = [k for k in list(merge_dict.keys()) if "R" not in k]
    keys = list(merge_dict.keys())
    k = [k for k in keys if "S" in k]
    values_dict = [merge_dict[v] for v in k]
    #keys = list(merge_dict.keys())

    values = set([item for sublist in values_dict for item in sublist])
    add_to_graph(G, values)
    DESTROY(G, k)
    return 

def commons(G, v):
    if len(v) < 1:
        return []
    elif len(v) == 1:
        return get_active_neighbors(G,v[0])
    else:
        neighs = []
        for v1 in v:
            neighs += [get_active_neighbors(G, v1)]
        return list(set(neighs[0]).intersection(*neighs))

def convert(G):
    E = []
    for v in activeVertices(G):
        for n in get_active_neighbors(G,v):
            E.append([v,n])

    E = sorted([sorted(i) for i in E])
    E = list(s for s,_ in itertools.groupby(E))

    undo = {}
    F = []
    for e in E:
        e0 = int(e[0].replace('S', ''))
        e1 = int(e[1].replace('S', ''))
        undo[e0] = e[0]
        undo[e1] = e[1]
        F.append([e0, e1])

    return F, undo

def undo(E, d):
    if d == {}:
        return E
    F = []
    for e in E:
        F += [d[e]]
    return F

#add an edge to the graph
def add_edge(G, e):
    G["vertices"][e[0]]["neighbors"].append(e[1])
    G["vertices"][e[1]]["neighbors"].append(e[0])
    
    deg = G["vertices"][e[0]]["active_degree"]
    G["DS"][deg].remove(e[0])
    G["vertices"][e[0]]["active_degree"] += 1
    
    if deg+1 in G["DS"]:
        G["DS"][deg+1].append(e[0])
    else:
        G["DS"][deg+1] = [e[0]]
    
    
    deg = G["vertices"][e[1]]["active_degree"]
    G["DS"][deg].remove(e[1])
    G["vertices"][e[1]]["active_degree"] += 1
    
    if deg+1 in G["DS"]:
        G["DS"][deg+1].append(e[1])
    else:
        G["DS"][deg+1] = [e[1]]
        
    G["num_edges"] += 1

    return

#delete edge from the graph
def delete_edge(G, e):
    #print(e,G["vertices"][e[0]]["active"], G["vertices"][e[1]]["active"])
    
    G["vertices"][e[0]]["neighbors"].remove(e[1])
    G["vertices"][e[1]]["neighbors"].remove(e[0])
    
    if G["vertices"][e[0]]["active"] and G["vertices"][e[1]]["active"]:
        deg = G["vertices"][e[0]]["active_degree"]
        G["DS"][deg].remove(e[0])
        G["vertices"][e[0]]["active_degree"] -= 1
        
        if deg-1 in G["DS"]:
            G["DS"][deg-1].append(e[0])
        else:
            G["DS"][deg-1] = [e[0]]

        deg = G["vertices"][e[1]]["active_degree"]
        G["DS"][deg].remove(e[1])
        G["vertices"][e[1]]["active_degree"] -= 1
        
        if deg-1 in G["DS"]:
            G["DS"][deg-1].append(e[1])
        else:
            G["DS"][deg-1] = [e[1]]
            
        G["num_edges"] -= 1
    
    elif G["vertices"][e[0]]["active"]:
        G["vertices"][e[1]]["active_degree"] -= 1
    elif G["vertices"][e[1]]["active"]:
        G["vertices"][e[0]]["active_degree"] -= 1
        
    #G["num_edges"] -= 1
    return

#delete a whole list of edges
def delete_edges(G, E):
    for e in E:
        delete_edge(G,e)

#einfache breitensuche
def bfs(G, start):
    visited = []
    Q = [start]
    while(len(Q)!=0):
        v = Q[0]
        if v not in visited:
            visited.append(v)
            neigh = get_active_neighbors(G,v)
            Q.extend(neigh)
        Q.remove(v)
    return visited

#connected components for undirected graph
def connected_components(G):
    stack = activeVertices(G)
    visited = []
    ssc = []
    while (len(stack)!=0):
        v = stack[0]
        if v not in visited:
            v_v = bfs(G, v)
            ssc.append(v_v)
            visited.extend(v_v)
        stack.remove(v)
    return ssc
