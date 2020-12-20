from preprocess import preprocess
from helps import delete_vertices, get_active_neighbors, activeVertices, DESTROY

def heuristic1(G):
    max_d = 0
    max_v = []
    for v in activeVertices(G):
        deg = G["vertices"][v]["active_degree"]
        if deg > max_d:
            max_d = deg
            max_v = [v]
        elif deg == max_d and deg!=0:
            max_v.append(v)
    delete_vertices(G,max_v)
    return max_v

def heuristic3(G):
    v_list = []
    for v in G["vertices"]:
        if G["vertices"][v]["active"]:
            if G["vertices"][v]["active_degree"] > 6:
                v_list += [v]
                delete_vertices(G, [v])
    v1, md = recprep(G,G["active_nodes"]-1)
    v_list += v1
    for v in G["vertices"]:
        if G["vertices"][v]["active"]:
            if G["vertices"][v]["active_degree"] <= 3:
                neig = get_active_neighbors(G,v)
                v_list += neig
                delete_vertices(G, neig)
    return v_list, md

def recprep(G,k):
    v_list = []
    merge_dict = {}
    cont = True
    while(cont):
        cont = False
        pre_v, _, _, md = preprocess(G, k)
        v_list += pre_v
        merge_dict.update(md)
        if len(pre_v) > 0:
            cont = True
    return v_list, merge_dict

def heuristic(G):
    v_list, merge_dict = heuristic3(G)   
    while G["active_nodes"] > 0:
        DESTROY(G, [x for x in G["vertices"] if not G["vertices"][x]["active"]])
        v_list2, merge_dict2 = recprep(G,G["active_nodes"]-1)
        v_list += v_list2
        merge_dict.update(merge_dict2)
        if G["active_nodes"] == 0:
            break
        v_list += heuristic1(G)

    return len(v_list), v_list, merge_dict
