from helps import delete_vertices, get_active_neighbors, addVertex, add_to_graph, DESTROY, merge, activeVertices, commons, add_edge
import settings
from matching import matching, bipartiteMatch
import math 
from collections import Counter
from clique_cover import clique_cover
import numpy as np

def domination_rule(G):
    v_list = []
    for v in activeVertices(G):
        if G["vertices"][v]["active"]:
            min_d = math.inf
            min_v = None
            for n in get_active_neighbors(G,v):
                deg = G["vertices"][n]["active_degree"]
                if deg < min_d:
                    min_d = deg
                    min_v = n
            if min_v is not None:
                for v2 in commons(G, [v]+[min_v]):
                    if hash(v) < hash(v2) and G["vertices"][v]["active"] and G["vertices"][v2]["active"] and v not in v_list and v2 not in v_list:
                        s1 = set(get_active_neighbors(G, v)+[v])
                        s2 = set(get_active_neighbors(G, v2)+[v2])
                        if s1.issubset(s2):
                            v_list.append(v2)
                        elif s2.issubset(s1):
                            v_list.append(v)      
    delete_vertices(G, v_list)
    return v_list

def preprocess(G, k):
    if k < 0:
        return [], [], k, {}
    v_list = []
    g_list = []
    merge_dict = {}
    cont = True
    while(cont):
        cont = False
        for v in activeVertices(G):
            if G["vertices"][v]["active"]:
                deg = G["vertices"][v]["active_degree"]
                if deg > k:
                    cont = True
                    delete_vertices(G, [v])
                    v_list.append(v)
                    k -= 1
                elif deg == 1:
                    cont = True
                    x = get_active_neighbors(G, v)[0]
                    delete_vertices(G, [v, x])
                    v_list.append(x)
                    g_list.append(v)
                    k -= 1
                elif deg == 0:
                    delete_vertices(G, [v])
                    g_list.append(v)
                elif deg == 2: 
                    cont = True
                    n = get_active_neighbors(G, v)
                    if n[1] in G["vertices"][n[0]]["neighbors"]: 
                        v_list.extend(n)
                        g_list.append(v)
                        delete_vertices(G, [v, n[0], n[1]])
                        k -= 2 
                    else:
                        v_new = merge(G, v, n[0], n[1])
                        v_list.append(v_new)
                        merge_dict[v_new] = [v] + n
                        k -= 1

    return v_list, g_list, k, merge_dict
    
    
def deg_3_independent_set(G):
    added_edges = []
    reduce_list = []
    g_list = []
    
    if 3 not in G["DS"]:
        return [], [], []
    
    for v in G["DS"][3]:
        if G["vertices"][v]["active"] and G["vertices"][v]["active_degree"]==3:
            n = get_active_neighbors(G, v)
            n0 = get_active_neighbors(G, n[0])
            n1 = get_active_neighbors(G, n[1])
            n2 = get_active_neighbors(G, n[2])
            
            
            #check independent set in n
            if n[0] not in n1 and n[1] not in n2 and n[2] not in n0:
                cont = True
                delete_vertices(G, [v])
                g_list.append(v)
                n0.remove(v)
                n1.remove(v)
                n2.remove(v)
                edges=[[n[0],n[1]], [n[1],n[2]]]
                edges.extend([[n[0], t] for t in n1 if t not in n0])
                edges.extend([[n[1], t] for t in n2 if t not in n1])
                edges.extend([[n[2], t] for t in n0 if t not in n2])
                added_edges.extend(edges)
                reduce_list.append([v, n[0], n[1], n[2]])
                for e in edges:
                    add_edge(G,e)
                
    return added_edges, reduce_list, g_list
    

#@profile
def unconfined(G):
    v_list = []
    for v in list(activeVertices(G)):
        if G["vertices"][v]["active"]:
            S = [v]
            minlen = math.inf
            u_final = None
            neighborsSall = [x for s in S for x in get_active_neighbors(G,s)] 
            neighborsS = list(set(neighborsSall))
            neighborsSwithS = list(set(neighborsS + S))
            cont = True
            while(cont):
                iterate = neighborsS
                for u in iterate:
                    neighborsu = get_active_neighbors(G,u)
                    if len(set(neighborsu).intersection(S)) == 1: #kann weg mit anderem iterate
                        cut = list(set(neighborsu)-set(neighborsSwithS))
                        if len(cut) < minlen:
                            minlen = len(cut)
                            u_final = u
                            cut_final = cut
                if u_final == None:
                    cont = False
                elif minlen == 0:
                    v_list += [v]
                    delete_vertices(G, [v])
                    cont = False
                elif minlen == 1:
                    S += cut_final 
                    neighborsSall = [x for s in S for x in get_active_neighbors(G,s)] 
                    neighborsSwithS = list(set(neighborsSall + S))
                    u_final = None
                    minlen = math.inf 
                else: 
                    cont = False
                
    return v_list


def two_clique_neigh(G, k, deg):
    v_list = []
    g_list = []
    added_edges = []
    reduce_list = []
    
    for v in G["vertices"]:
        if G["vertices"][v]["active"]:
            neigh = get_active_neighbors(G,v)
            if len(neigh) <= deg:
                cc = clique_cover(G, neighbors=neigh)
                
                if len(cc) == 2:
                    c1_ind = np.argmax([len(cc[0]), len(cc[1])])
                    c1 = cc[c1_ind]
                    c2 = cc[1-c1_ind]
                    
                    M = []
                    for v1 in c1:
                        for v2 in c2:
                            if v2 not in G["vertices"][v1]["neighbors"]: #no need to check for active, because they are all active
                                M.append([v1,v2])
                    sc1 = set(c1)
                    suitable = True
                    for m in M:
                        try:
                            sc1.remove(m[0])
                        except:
                            suitable = False
                        
                    if not suitable or len(sc1) > 0:
                        continue
                
                    delete_vertices(G, c2)
                    delete_vertices(G, [v])
                    
                    v_list.extend(c2)
                    g_list.append(v) 
                    k -= len(c2)
                    
                    reduce_list.append([v, c1, M])
                    
                    for m in M:
                        neigh = get_active_neighbors(G, m[1])
                        for n in neigh:
                            if n not in G["vertices"][m[0]]["neighbors"]:
                                added_edges.append([m[0],n])
                                add_edge(G, [m[0],n])
                                
    return v_list, g_list, k, added_edges, reduce_list

def alternatingBFS(G, L, R, M):
    visited = []
    Q = [v for v in L if v in G and v not in M]
    while(len(Q)!=0):
        v = Q[0]
        if v not in visited:
            visited.append(v)
            
            if v in L:
                neigh = [n for n in G[v] if G[v]!=n]
                
            if v in R:
                neigh = [M[v]]
                
            Q.extend(neigh)
        Q.remove(v)
    return visited

def crown(G):
    
    M = matching(G)
    A = list(M.keys())
    B = [v for v in activeVertices(G) if v not in A]
    EAB = [[a,b] for a in A for b in get_active_neighbors(G, a) if b in B] #this takes ages
    graph = {}
    for a in A:
        graph[a] = []
    for e in EAB:
        if e[0] in graph:
            graph[e[0]].append(e[1])

            
    M, _, _ = bipartiteMatch(graph)

    
    M1 = {}
    for m in M:
        M1[m] = M[m]
        M1[M[m]] = m
        
        
    for e in EAB:
        if e[1] in graph:
            graph[e[1]].append(e[0])
        else: 
            graph[e[1]] = [e[0]]
            

    
    Z = alternatingBFS(graph, A, B, M1)
    
    X = [v for v in A if v not in Z] + [v for v in B if v in Z]
    
    AX = [v for v in A if v in X]
    B0 = [v for v in B if v not in X]
    
    
    
    return AX, B0

