import sys
import copy
from matching import matching
from lp_solver import lp_solver2, lp_solver
from clique_cover import clique_cover
from preprocess import preprocess, domination_rule, unconfined, deg_3_independent_set, two_clique_neigh, crown
from helps import read_input, delete_vertices, add_to_graph, get_active_neighbors, activeVertices, DESTROY, reset, connected_components, delete_edges, add_edge
from flow import flow
from collections import Counter
import settings
from heuristic import heuristic
import operator
import inspect

def output_VC(v_list, merge_dict):
    cont = True
    while(len(merge_dict) > 0):
       # while(cont):
       #     cont = False
       #     a = list(merge_dict)
       #     filtered = [v for v in v_list if 'S' in v]
       #     counts = Counter(filtered) 
       #     #import pdb; pdb.set_trace()
       #     twice = list(set([x for x in a if counts[x] == 2]))
       #     zero= list(set([x for x in a if counts[x] == 0]))
       #     for z in zero:
       #         if "S" in z:
       #             merge_dict.pop(z)
       #     for m in twice: 
       #         v_list.remove(m)
       #         v_list.remove(m)
       #         v_list.extend(merge_dict.pop(m)[1:])
       #         cont = True  
       # cont = True
        m_v = list(merge_dict.keys())
        #import pdb; pdb.set_trace()
        if len(m_v) == 0: 
            break
        #print("#mv", m_v[-1])
        if "S" in m_v[-1]:
            #print("#S", m_v[-1], merge_dict[m_v[-1]])
            count = len([v for v in v_list if v == m_v[-1]])
            if count == 2:
                v_list.remove(m_v[-1])
                v_list.remove(m_v[-1])
                v_list.extend(merge_dict.pop(m_v[-1])[1:])
            if count == 1:
                v_list.append((merge_dict.pop(m_v[-1]))[0])
                v_list.remove(m_v[-1])
            if count == 0:
                merge_dict.pop(m_v[-1])
        elif "R" in m_v[-1]:
            reduce_list = merge_dict.pop(m_v[-1])
            #print("#RRR", reduce_list)
            for r_ind in range(len(reduce_list)):
                r = reduce_list[-r_ind-1]
                #print("#R",r)
                count = 0
                in_list = []
                for r1 in r[1:]:
                    if r1 in v_list:
                        if "S" in r1:
                            c = len([v for v in v_list if v == r1])
                            if c == 2:
                                count += 1
                                in_list.append(r1)
                        else:
                            count += 1
                            in_list.append(r1)
                        
                #print(in_list)
                if count == 1:
                    v_list.remove(in_list[0])
                    v_list.append(r[0])
                if count == 2:
                    v_list.append(r[0])
                    for r1 in range(1, len(r)):
                        if r[r1] not in in_list:
                            if r1 == 1:
                                v_list.remove(r[2])
                            if r1 == 2:
                                v_list.remove(r[3])
                            if r1 == 3:
                                v_list.remove(r[1])
                                
        elif "T" in m_v[-1]:
            reduce_list = merge_dict.pop(m_v[-1])
            #print("#TTT", reduce_list)
            for r_ind in range(len(reduce_list)):
                r = reduce_list[-r_ind-1]
                #print("#T",r)
                non_selected = []
                #import pdb; pdb.set_trace()
                for v in r[1]: #iterate over c1
                    if v not in v_list:
                        non_selected.append(v)
                    else:
                        if "S" in v:
                            c = len([vert for vert in v_list if vert == v])
                            if c == 1:
                                non_selected.append(v)
                #print("#non_selected", non_selected)
                    
                if len(non_selected) > 0: #only 1 vertex at most in this list
                    v_list.append(r[0])
                    for m in r[2]:
                        if m[0] == non_selected[0]:
                            v_list.remove(m[1])
                

    v_list.sort(key=int)
    print("#", len(v_list))
    for v in v_list:
        print(v)
        #pass

    return v_list


def constrained_branching(G, P, c, u, c_list):
    '''
    TODO reset merge ?
    TODO keep current solution

    '''
    settings.recursive_steps += 1
    k = len(u)
    
    #if settings.recursive_steps%100000==0:print(settings.recursive_steps)
    
    
  
    #DATAREDUCTION--------------------------------------------------------    
    if settings.freq_by_rec_steps == True:
        freq_count = settings.recursive_steps
    if settings.freq_by_rec_depth == True:
        freq_count = len(inspect.stack())
    
    #allways do the easy preprocess
    v_list, g_list, k, merge_dict = preprocess(G, k)
    v_dom , v_unc = [], []
    lp_g_list = []
    lp_v_list = []
    
    added_edges = []
    reduce_list = []
    
    influenced = False #was the graph influenced by other rules
    
    if freq_count % settings.branch_deg_3_independent== 0:       
        e1 = G["num_edges"]
        added_edges, reduce_list, g_list2 = deg_3_independent_set(G)
        if len(reduce_list) > 0:
            mrl = {}
            g_list.extend(g_list2)
            mrl["R"+str(settings.recursive_steps)] = reduce_list
            merge_dict.update(mrl)
    
    if freq_count % settings.branch_two_clique == 0:
        v_list_tc, g_list_tc, k, added_edges2, reduce_list = two_clique_neigh(G, k, settings.branch_two_clique_degree)
        if len(reduce_list) > 0:
            v_list.extend(v_list_tc)
            g_list.extend(g_list_tc)
            added_edges.extend(added_edges2)
            mrt = {}
            mrt["T"+str(settings.recursive_steps)] = reduce_list
            merge_dict.update(mrt)
    
    if freq_count % settings.branch_domination == 0: 
        influenced = True
        v_dom = domination_rule(G)
        k -= len(v_dom)
        v_list += v_dom
        
    if freq_count % settings.branch_unconfined == 0:
        influenced = True
        v_unc = unconfined(G)
        k -= len(v_unc)
        v_list += v_unc
        
    if freq_count % settings.branch_crowns == 0:
        influenced = True
        v_crown, g_crown = crown(G)
        #print("#", len(v_crown), v_crown, g_crown)
        k -= len(v_crown)
        v_list += v_crown
        g_list += g_crown
        delete_vertices(G, v_crown+g_crown)
        
       
    if freq_count % settings.branch_lp == 0:
        influenced = True
        lp_v_list, lp_g_list = lp_solver2(G, exhaustivly=settings.branch_lp_exhaustivly)
        k -= len(lp_v_list)
        v_list += lp_v_list
        g_list += lp_g_list
        delete_vertices(G, lp_v_list+lp_g_list)
    
    
    if freq_count % settings.branch_second_prep == 0 and influenced==True:
        v_list3, g_list2, k, merge_dict2 = preprocess(G, k)
        v_list += v_list3
        g_list += g_list2
        merge_dict.update(merge_dict2)
        v_dom = domination_rule(G)
        k -= len(v_dom)
        v_list += v_dom
        
    
    
    c_list.extend(v_list)
    c += len(v_list)
    
    
    #PACKING CONSTRAINTS--------------------------------------------------------------------------
    
    verticesList = activeVertices(G) #actually take v_list
    for p in P:
        count = 0
        for x in p:
            if x in c_list:
                count += 1
        if count == len(p):
            add_to_graph(G, v_list+g_list)
            delete_edges(G, added_edges)
            reset(G, merge_dict)
            return u, {}
        
    #RECURSION ROOTS------------------------------------------------------------------------------
    
    clique_c = clique_cover(G)
    l = G["active_nodes"] - len(clique_c)
    
    if len(c_list) + l >= len(u):
        add_to_graph(G, v_list+g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)
        return u, {}
    
    if G["num_edges"] == 0:
        add_to_graph(G, v_list+g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)
        return c_list, merge_dict
      
      
    
    cc = connected_components(G)
    verticesList = activeVertices(G)
    md1 = {}
    u_changed = u
    
    if len(cc) > 1:
        for cc1 in cc:
            to_del = [n for n in verticesList if n not in cc1] #only cc1 remains in G
            delete_vertices(G, to_del)
            u_c = [u1 for u1 in u_changed if u1 not in c_list]
            u_changed = u_c
            c1, md = constrained_branching(G, P, 0, u_changed, [])
            #c += c1
            md1.update(md)
            c_list.extend(c1)
            add_to_graph(G, to_del)
            
        add_to_graph(G, v_list+g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)
        
        #c_list = list(set(c_list))
        if len(c_list) <= len(u):
            merge_dict.update(md1)
            return c_list, merge_dict
        else:
            return u, {}
    
        
    #Branching--------------------------------------------------------------
    
    #get max_deg vertex + neighborhood
    max_d = 0
    max_v = None
    for v in G["vertices"]:
        if G["vertices"][v]["active"]:
            deg = G["vertices"][v]["active_degree"]
            if deg > max_d:
                max_d = deg
                max_v = v
    neighbors = get_active_neighbors(G, max_v)


    #first branch + reverting it
    delete_vertices(G, [max_v])
    P1 = P 
    P1.append(neighbors)
    new_c1_list = c_list+[max_v]
    u1, md = constrained_branching(G, P1, c+1, u , new_c1_list) 
    #rmd1 = {}
    #rmd1.update(merge_dict)
    #rmd1.update(md)
    rmd1 = dict(merge_dict, **md) 
    add_to_graph(G, [max_v])  

    #second branch + reverting it
    delete_vertices(G, neighbors+[max_v])
    #P2 = P
    #P2.append([max_v])
    new_c2_list = c_list+neighbors
    u2, md = constrained_branching(G, [], c+len(neighbors), u1, new_c2_list)  
    rmd2 = dict(merge_dict, **md)
    add_to_graph(G, neighbors+[max_v])  


    #reset G
    add_to_graph(G, v_list+g_list)  
    delete_edges(G, added_edges)
    reset(G, merge_dict)
    
    #return
    if len(u1) <= len(u2):
        return u1, rmd1
    else: 
        return u2, rmd2
    
    
def branch(G, k):
    settings.recursive_steps += 1
  
    #DATAREDUCTION--------------------------------------------------------
    
    s = 0
    for v in activeVertices(G):
        s += len(get_active_neighbors(G,v))
    s /= 2
    if s != G["num_edges"]:
        print("#kack", s, G["num_edges"])
    
    if settings.freq_by_rec_steps == True:
        freq_count = settings.recursive_steps
    if settings.freq_by_rec_depth == True:
        freq_count = len(inspect.stack())
    
    #allways do the easy preprocess
    v_list, g_list, k, merge_dict = preprocess(G, k)
    v_dom , v_unc = [], []
    lp_g_list = []
    lp_v_list = []
    
    added_edges = []
    reduce_list = []
    
    influenced = False #was the graph influenced by other rules
    
    if freq_count % settings.branch_deg_3_independent== 0:       
        e1 = G["num_edges"]
        added_edges_3, reduce_list, g_list2 = deg_3_independent_set(G)
        if len(reduce_list) > 0:
            mrl = {}
            added_edges.extend(added_edges_3)
            g_list.extend(g_list2)
            mrl["R"+str(settings.recursive_steps)] = reduce_list
            merge_dict.update(mrl)
    
    if freq_count % settings.branch_two_clique == 0:
        v_list_tc, g_list_tc, k, added_edges2, reduce_list = two_clique_neigh(G, k, settings.branch_two_clique_degree)
        if len(reduce_list) > 0:
            v_list.extend(v_list_tc)
            g_list.extend(g_list_tc)
            added_edges.extend(added_edges2)
            mrt = {}
            mrt["T"+str(settings.recursive_steps)] = reduce_list
            merge_dict.update(mrt)
    
    if freq_count % settings.branch_domination == 0: 
        influenced = True
        v_dom = domination_rule(G)
        k -= len(v_dom)
        v_list += v_dom
        
    if freq_count % settings.branch_unconfined == 0:
        influenced = True
        v_unc = unconfined(G)
        k -= len(v_unc)
        v_list += v_unc
        
    if freq_count % settings.branch_crowns == 0:
        influenced = True
        v_crown, g_crown = crown(G)
        #print("#", len(v_crown), v_crown, g_crown)
        k -= len(v_crown)
        v_list += v_crown
        g_list += g_crown
        delete_vertices(G, v_crown+g_crown)
        
       
    if freq_count % settings.branch_lp == 0:
        influenced = True
        lp_v_list, lp_g_list = lp_solver2(G, exhaustivly=settings.branch_lp_exhaustivly)
        k -= len(lp_v_list)
        v_list += lp_v_list
        g_list += lp_g_list
        delete_vertices(G, lp_v_list+lp_g_list)
    
    
    if freq_count % settings.branch_second_prep == 0 and influenced==True:
        v_list3, g_list2, k, merge_dict2 = preprocess(G, k)
        v_list += v_list3
        g_list += g_list2
        merge_dict.update(merge_dict2)
        v_dom = domination_rule(G)
        k -= len(v_dom)
        v_list += v_dom


    #RECURSION ROOTS-----------------------------------------------------------------------

    if G["num_edges"] > k**2 or G["active_nodes"] > (k**2 + k):
        add_to_graph(G, v_list+g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)
        return None, None
    
    if k < 0:
        add_to_graph(G, v_list+g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)
        return None, None
     
    if G["active_nodes"] == 0:
        return v_list, merge_dict

    if G["active_nodes"] <= k:
        return v_list + activeVertices(G), merge_dict

    if k == 0:
        add_to_graph(G, v_list+g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)
        return None, None



    #BRANCHING------------------------------------------------------------------------

    max_d = 0
    max_v = None
    for v in G["vertices"]:
        if G["vertices"][v]["active"]:
            deg = G["vertices"][v]["active_degree"]
            if deg > max_d:
                max_d = deg
                max_v = v

    delete_vertices(G, [max_v])
    VC, md = branch(G, k-1)  
    if VC is not None:
        rmd = dict(merge_dict, **md)
        return VC + v_list + [max_v], rmd
    add_to_graph(G, [max_v])  

    neighbors = get_active_neighbors(G, max_v)
    delete_vertices(G, neighbors)
    VC, md = branch(G, k-len(neighbors))  
    if VC is not None:
        rmd = dict(merge_dict, **md)
        return VC + v_list + neighbors, rmd
    add_to_graph(G, neighbors)  

    add_to_graph(G, v_list+g_list)  
    delete_edges(G, added_edges)
    reset(G, merge_dict)
    return None, None


def main():
    '''
    T O D O - L I S T
    
    NEW FEATURES:
        TODO implement Crown rule
        TODO implement relaxed crwon rule
        TODO SMAC testing
    
    
    HALFWAY IMPLEMENTED:
        TODO degree table -> use it
        
        
    CLEAN-UPS: (no new features, but makes codes faster)
        TODO make sure we dont prep 2 times after another (2 times cont || before and in a loop)
        TODO split preprocess in its single parts
        TODO clique_cover only consider joinable cliques
        TODO clean up help functions
        TODO use itertools
        TODO save list of active vertices in G
        TODO profiling
        
        TODO more constraints for constrained_branching
        
    '''
    arguments = sys.argv[1:]
    if len(arguments)>1:
        if arguments[0] == "True":
            settings.freq_by_rec_depth = True
            settings.freq_by_rec_steps = False
        else:
            settings.freq_by_rec_steps = True
            settings.freq_by_rec_depth = False
        
        settings.use_constrained_branching = False
        settings.search_binary = False
        settings.search_linear1 = False
        settings.search_linear2 = False
        
        if arguments[1] == "sb":
            settings.search_binary = True
        elif arguments[1] == "sl1":
            settings.search_linear1 = True
        elif arguments[1] == "sl2":
            settings.search_linear2 = True
        else:
            settings.use_constrained_branching = True
            
            
        settings.branch_domination = int(arguments[2])
        settings.branch_crowns = int(arguments[3])
        settings.branch_lp = int(arguments[4])
        settings.unconfined = int(arguments[5])
        settings.branch_second_prep = int(arguments[6])

        if arguments[7] == "True":
            settings.branch_lp_exhaustivly = True
        else:
            settings.branch_lp_exhaustivly = False
            
        settings.branch_two_clique = int(arguments[8])
        settings.branch_two_clique_degree = int(arguments[9])
        settings.branch_deg_3_independent = int(arguments[10])
    

    sys.setrecursionlimit(10000)
    G = read_input(sys.stdin)
    
    G_test = copy.deepcopy(G)

    v_list, g_list, merge_dict = [], [], {}

    selfs = []
    for v in activeVertices(G):
        if v in G["vertices"][v]["neighbors"]:
            selfs += [v]

    v_list += selfs
    DESTROY(G, selfs)

    k = len(G["vertices"])-1


    #INITIAL PREPROCESS--------------------------------------------------------

    cont = True
    while(cont):
        cont = False
        pre_v, pre_g, k, merge_dict2 = preprocess(G, k)
        dom_v = domination_rule(G)
        v_list += pre_v + dom_v # + unc
        g_list += pre_g
        merge_dict.update(merge_dict2)
        if len(pre_v+pre_g+dom_v) > 0: # + unc
            cont = True
            k -= len(dom_v) # + unc

    if G["active_nodes"] == 0:
        print('#recursive steps: 0')
        output_VC(v_list, merge_dict)
        return

    md = merge_dict 

    to_delete = [x for x in G["vertices"] if not G["vertices"][x]["active"]]
    DESTROY(G, to_delete)

    lp_v_list, lp_g_list = lp_solver2(G)
    v_list += lp_v_list
    DESTROY(G, (lp_v_list+lp_g_list))
    
    if G["active_nodes"] == 0:
        print('#recursive steps: 0')
        output_VC(v_list, merge_dict)
        return
    
    unc = unconfined(G)
    k -= len(unc)
    pre_v, pre_g, k, merge_dict2 = preprocess(G, k)
    merge_dict.update(merge_dict2)
    v_list += unc + pre_v
    g_list += pre_g
    
    if G["active_nodes"] == 0:
        print('#recursive steps: 0')
        output_VC(v_list, merge_dict)
        return
    
    #delete all unactive vertices before branching
    to_delete = [x for x in G["vertices"] if not G["vertices"][x]["active"]]
    DESTROY(G, to_delete)
    
    max_k = int(len(matching(G)))
    min_k = G["active_nodes"] - len(clique_cover(G))  
    
    G3 = copy.deepcopy(G)
    max_k, upper_bound, merge_dict_heu = heuristic(G3)
    
    
    #SEARCH FOR K---------------------------------------------------------------
    

    if settings.use_constrained_branching:
        print("#start constrained_branching")
        VC, merge_dict2 = constrained_branching(G, [], 0, upper_bound, [])
        keys2 = list(merge_dict2.keys())
        for m in list(merge_dict_heu.keys()):
            if m in keys2:
                merge_dict_heu.pop(m)
        merge_dict_heu.update(merge_dict2)
        merge_dict.update(merge_dict_heu)

    else: #normal branching
        VC = None
        #binary search for k
        if settings.search_binary:
            k = int((min_k+max_k)/2)
            while (min_k != max_k):
                print("#k =", k)
                G2 = copy.deepcopy(G)
                VC, merge_dict = branch(G2, k)
                if VC is None:
                    min_k = k+1
                    k = int((k+max_k)/2)
                else:
                    max_k = k
                    k = int((min_k+k)/2)

            if VC is None:
                VC, merge_dict = branch(G, min_k)
            
        #linear search (k+=1)
        if settings.search_linear1:
            k = min_k
            while (VC == None):
                G2 = copy.deepcopy(G)
                VC, merge_dict = branch(G2, k)
                k+=1
                
        #linear search (k+=2)
        if settings.search_linear2:
            k = min_k
            while (VC == None):
                G2 = copy.deepcopy(G)
                VC, merge_dict = branch(G2, k)
                k+=2
            
            G2 = copy.deepcopy(G)
            VC2, merge_dict2 = branch(G2, k-3) 
            
            if VC2 is not None:
                VC = VC2
                merge_dict = merge_dict2


    #OUTPUT---------------------------------------------------------------------
    
    if VC == None:
        print("#error")
        while(True):
            pass
    
    VC += v_list 

    print('#recursive steps:', settings.recursive_steps)
    print("#|VC| =", len(VC))

    md.update(merge_dict) 
    test = output_VC(VC, md)

    return

settings.init()
main()
