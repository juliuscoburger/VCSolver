from pulp import *
from helps import read_input,read_edges,addVertex, DESTROY, activeVertices, get_active_neighbors
from matching import matching, bipartiteMatch
import sys

def lp_solver(G):
    Edges = []
    for v in G["vertices"]:
        for e in G["vertices"][v]["neighbors"]:
            Edges.append([v, e])

    node_vars = LpVariable.dicts("x", list(G["vertices"].keys()), lowBound=0, upBound=1)

    prob = LpProblem("VC", LpMinimize)

    prob += lpSum([node_vars[i] for i in list(G["vertices"].keys())])

    for e in Edges:
        prob += lpSum([node_vars[i] for i in e]) >= 1

    status = prob.solve()
    
    v_list = []
    g_list = []

    for v in prob.variables():
        name = v.name
        name = name.replace("_","").replace("x","")
        if v.varValue is not None and v.varValue < 0.5:
            g_list.append(name)
        if v.varValue is not None and v.varValue > 0.5:
            v_list.append(name)

    return v_list, g_list

def reverse_graph(G):
    graph = {}
    vertices = G.keys()
    for v in vertices:
        graph[v] =  []
    for v in vertices:
        for n in G[v]:
            graph[n].append(v)
    return graph
    
def bfs(G, start):
    visited = []
    Q = [start]
    while(len(Q)!=0):
        v = Q[0]
        if v not in visited:
            visited.append(v)
            neigh = G[v]
            Q.extend(neigh)
        Q.remove(v)
    return visited

def dfs(G, start, all_visitied = []):
    visited = []
    Q = [start]
    while(len(Q)!=0):
        v = Q[-1]
        if v not in visited and v not in all_visitied:
            visited.append(v)
            neigh = G[v]
            Q.extend(neigh)
        Q.remove(v)
    return visited

def out(output):
    v_list, g_list = [], []
    for o in output.keys():
        if output[o] == 0:
            g_list.append(o)
        if output[o] == 1:
            v_list.append(o)
    return v_list, g_list

def strongly_connected_components(G):
    stack = []
    
    for v in G:
        if v not in stack:
            r = dfs(G, v, stack)
            stack.extend(r)
            
    visited = []
    ssc = []
    graph = reverse_graph(G)
    
    while (len(stack)!=0):
        v = stack[0]
        if v not in visited:
            v_v = dfs(graph, v, visited)
            #print("stk_op", v, v_v)
            ssc.append(v_v)
            visited.extend(v_v)
        stack.remove(v)
    return ssc



def lp_solver2(G, exhaustivly=True):

    verticesList = activeVertices(G)
    
    verticesList2 = []
    graph = {}
    for v in verticesList:
        neigh = get_active_neighbors(G,v)
        if len(neigh) > 0:
            verticesList2.append(v)
            graph["l"+v] = ["r"+ver for ver in neigh]
            graph["r"+v] = []
    
    verticesList = verticesList2
    
    if len(verticesList)==0:
        return [], []
    
    match, _, _ = bipartiteMatch(graph)

    for m in list(match.keys()):
        x = match[m]
        match[x] = m
    

    #add edges starting in s and t
    s_neighbors = ["l"+v for v in verticesList if ("l"+v) not in match]
    t_neighbors = ["r"+v for v in verticesList if ("r"+v) in match] 
    
    graph["s"] = s_neighbors
    graph["t"] = t_neighbors
    
   
    for v in verticesList:
        #add edges back to s and t
        if ("l"+v) in match:
            graph["l"+v].append("s")
        if ("r"+v) not in match:
            graph["r"+v].append("t")
            
         #add back edges in between L and R
        if ("l"+v) in match:
            #print(match["l"+v], "l"+v)
            graph[match["l"+v]].append("l"+v)


    reach = bfs(graph, "s")
    

    output={}
    del_list = []
    
    for v in verticesList:
        if v not in del_list:
            if ("l"+v) in reach and ("r"+v) not in reach:
                output[v] = 0
                del_list.append(v)
            elif ("l"+v) not in reach and ("r"+v) in reach:
                output[v] = 1
                del_list.append(v)
            else:
                output[v] = 0.5
            
    
    if not exhaustivly:
        return out(output)
    
    
    while(True):
        for v in (["l"+v1 for v1 in del_list]+["r"+v2 for v2 in del_list]):
            del graph[v]
        
        for v in graph:
            neigh = []
            neigh.extend(graph[v])
            for n in neigh:
                if n not in graph:
                    graph[v].remove(n)
              
        if len(graph) <= 2: #only s+t left
            return out(output)
        
        cc = strongly_connected_components(graph)
        
        cc_use = None
        #print("cc's",cc)
        for c in cc:
            usable=True
            
            for v in c:
                for n in graph[v]:
                    if n != "s" and n != "t" and n not in c:
                        usable = False
            
            if not usable:
                break
            
            for v in verticesList:
                in_c = 0
                if "l"+v in c:
                    in_c += 1
                if "r"+v in c:
                    in_c += 1   
                if in_c == 2:
                    usable=False
                    break
                
            if not usable:
                break
            
            cc_use = c
            break
            
        cc = cc_use
        
        #print(cc)
        
        if cc == None:
            return out(output)
        
        
        l_cc = [v for v in cc if v[0]=="l"]
        r_cc = [v for v in cc if v[0]=="r"]
        
        
        del_list =[]
        
        for i in l_cc:
            output[i[1:]] = 0
            del_list.append(i[1:])
        for i in r_cc:
            output[i[1:]] = 1
            del_list.append(i[1:])
    
    return out(output)

