import inspect

import settings
from clique_cover import clique_cover
from helps import delete_vertices, add_to_graph, get_active_neighbors, activeVertices, reset, connected_components, \
    delete_edges
from lp_solver import lp_solver2
from preprocess import preprocess_degree, domination_rule, unconfined, deg_3_independent_set, two_clique_neigh, crown


def data_reduction(G, k):
    if settings.freq_by_rec_steps:
        freq_count = settings.recursive_steps
    if settings.freq_by_rec_depth:
        freq_count = len(inspect.stack())

    v_list, g_list, k, merge_dict = preprocess_degree(G, k)
    added_edges = []

    influenced = False  # was the graph influenced by other rules

    if freq_count % settings.branch_deg_3_independent == 0:
        e1 = G["num_edges"]
        added_edges, reduce_list, g_list2 = deg_3_independent_set(G)
        if len(reduce_list) > 0:
            mrl = {}
            g_list.extend(g_list2)
            mrl["R" + str(settings.recursive_steps)] = reduce_list
            merge_dict.update(mrl)

    if freq_count % settings.branch_two_clique == 0:
        v_list_tc, g_list_tc, k, added_edges2, reduce_list = two_clique_neigh(G, k, settings.branch_two_clique_degree)
        if len(reduce_list) > 0:
            v_list.extend(v_list_tc)
            g_list.extend(g_list_tc)
            added_edges.extend(added_edges2)
            mrt = {}
            mrt["T" + str(settings.recursive_steps)] = reduce_list
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
        k -= len(v_crown)
        v_list += v_crown
        g_list += g_crown
        delete_vertices(G, v_crown + g_crown)

    if freq_count % settings.branch_lp == 0:
        influenced = True
        lp_v_list, lp_g_list = lp_solver2(G, exhaustivly=settings.branch_lp_exhaustivly)
        k -= len(lp_v_list)
        v_list += lp_v_list
        g_list += lp_g_list
        delete_vertices(G, lp_v_list + lp_g_list)

    if freq_count % settings.branch_second_prep == 0 and influenced:
        v_list3, g_list2, k, merge_dict2 = preprocess_degree(G, k)
        v_list += v_list3
        g_list += g_list2
        merge_dict.update(merge_dict2)
        v_dom = domination_rule(G)
        k -= len(v_dom)
        v_list += v_dom

    return v_list, g_list, merge_dict, added_edges, k


def constrained_branching(G, P, c, u, c_list):
    '''
    TODO reset merge ?
    TODO keep current solution

    '''
    settings.recursive_steps += 1
    k = len(u)

    # if settings.recursive_steps%100000==0:print(settings.recursive_steps)

    # DATAREDUCTION--------------------------------------------------------
    v_list, g_list, merge_dict, added_edges, k = data_reduction(G, k)

    c_list.extend(v_list)
    c += len(v_list)

    # PACKING CONSTRAINTS--------------------------------------------------------------------------

    for p in P:
        count = 0
        for x in p:
            if x in c_list:
                count += 1
        if count == len(p):
            add_to_graph(G, v_list + g_list)
            delete_edges(G, added_edges)
            reset(G, merge_dict)
            return u, {}

    # RECURSION ROOTS------------------------------------------------------------------------------

    clique_c = clique_cover(G)
    l = G["active_nodes"] - len(clique_c)

    if len(c_list) + l >= len(u):
        add_to_graph(G, v_list + g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)
        return u, {}

    if G["num_edges"] == 0:
        add_to_graph(G, v_list + g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)
        return c_list, merge_dict

    cc = connected_components(G)
    verticesList = activeVertices(G)
    md1 = {}
    u_changed = u

    if len(cc) > 1:
        for cc1 in cc:
            to_del = [n for n in verticesList if n not in cc1]  # only cc1 remains in G
            delete_vertices(G, to_del)
            u_c = [u1 for u1 in u_changed if u1 not in c_list]
            u_changed = u_c
            c1, md = constrained_branching(G, P, 0, u_changed, [])
            # c += c1
            md1.update(md)
            c_list.extend(c1)
            add_to_graph(G, to_del)

        add_to_graph(G, v_list + g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)

        if len(c_list) <= len(u):
            merge_dict.update(md1)
            return c_list, merge_dict
        else:
            return u, {}

    # Branching--------------------------------------------------------------

    max_v, max_d = get_max_deg_vertex(G)
    neighbors = get_active_neighbors(G, max_v)

    delete_vertices(G, [max_v])
    P1 = P
    P1.append(neighbors)
    new_c1_list = c_list + [max_v]
    u1, md = constrained_branching(G, P1, c + 1, u, new_c1_list)
    rmd1 = dict(merge_dict, **md)
    add_to_graph(G, [max_v])

    delete_vertices(G, neighbors + [max_v])
    new_c2_list = c_list + neighbors
    u2, md = constrained_branching(G, [], c + len(neighbors), u1, new_c2_list)
    rmd2 = dict(merge_dict, **md)
    add_to_graph(G, neighbors + [max_v])

    # reset G
    add_to_graph(G, v_list + g_list)
    delete_edges(G, added_edges)
    reset(G, merge_dict)

    # return
    if len(u1) <= len(u2):
        return u1, rmd1
    else:
        return u2, rmd2


def branch(G, k):
    settings.recursive_steps += 1
    v_list, g_list, merge_dict, added_edges, k = data_reduction(G, k)

    # RECURSION ROOTS-----------------------------------------------------------------------
    if G["num_edges"] > k ** 2 or G["active_nodes"] > (k ** 2 + k):
        add_to_graph(G, v_list + g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)
        return None, None

    if k < 0:
        add_to_graph(G, v_list + g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)
        return None, None

    if G["active_nodes"] == 0:
        return v_list, merge_dict

    if G["active_nodes"] <= k:
        return v_list + activeVertices(G), merge_dict

    if k == 0:
        add_to_graph(G, v_list + g_list)
        delete_edges(G, added_edges)
        reset(G, merge_dict)
        return None, None

    # BRANCHING------------------------------------------------------------------------
    max_v, max_d = get_max_deg_vertex(G)

    delete_vertices(G, [max_v])
    vertex_cover, md = branch(G, k - 1)
    if vertex_cover is not None:
        rmd = dict(merge_dict, **md)
        return vertex_cover + v_list + [max_v], rmd
    add_to_graph(G, [max_v])

    neighbors = get_active_neighbors(G, max_v)
    delete_vertices(G, neighbors)
    vertex_cover, md = branch(G, k - len(neighbors))
    if vertex_cover is not None:
        rmd = dict(merge_dict, **md)
        return vertex_cover + v_list + neighbors, rmd
    add_to_graph(G, neighbors)

    add_to_graph(G, v_list + g_list)
    delete_edges(G, added_edges)
    reset(G, merge_dict)
    return None, None


def get_max_deg_vertex(graph: dict):
    max_d = 0
    max_v = None
    for v in graph["vertices"]:
        if graph["vertices"][v]["active"]:
            deg = graph["vertices"][v]["active_degree"]
            if deg > max_d:
                max_d = deg
                max_v = v
    return max_v, max_d
