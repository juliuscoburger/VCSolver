import sys
import copy
from lp_solver import lp_solver2
from clique_cover import clique_cover
from preprocess import preprocess_degree, domination_rule, unconfined
from helps import read_input, activeVertices, DESTROY
import settings
from heuristic import heuristic

from branching import constrained_branching, branch


def output_VC(v_list, merge_dict):
    while len(merge_dict) > 0:

        m_v = list(merge_dict.keys())
        if len(m_v) == 0:
            break
        if "S" in m_v[-1]:
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
            for r_ind in range(len(reduce_list)):
                r = reduce_list[-r_ind - 1]
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
            for r_ind in range(len(reduce_list)):
                r = reduce_list[-r_ind - 1]
                non_selected = []
                for v in r[1]:  # iterate over c1
                    if v not in v_list:
                        non_selected.append(v)
                    else:
                        if "S" in v:
                            c = len([vert for vert in v_list if vert == v])
                            if c == 1:
                                non_selected.append(v)

                if len(non_selected) > 0:  # only 1 vertex at most in this list
                    v_list.append(r[0])
                    for m in r[2]:
                        if m[0] == non_selected[0]:
                            v_list.remove(m[1])

    v_list.sort(key=int)
    print("#", len(v_list))
    for v in v_list:
        print(v)

    return v_list


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

    # Set configurations
    arguments = sys.argv[1:]
    if len(arguments) > 1:
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

    # Run
    sys.setrecursionlimit(10000)
    G = read_input(sys.stdin)

    v_list, g_list, merge_dict = [], [], {}

    selfs = []
    for v in activeVertices(G):
        if v in G["vertices"][v]["neighbors"]:
            selfs += [v]

    v_list += selfs
    DESTROY(G, selfs)

    k = len(G["vertices"]) - 1

    # INITIAL PREPROCESS--------------------------------------------------------
    cont = True
    while cont:
        cont = False
        pre_v, pre_g, k, merge_dict2 = preprocess_degree(G, k)
        dom_v = domination_rule(G)
        v_list += pre_v + dom_v
        g_list += pre_g
        merge_dict.update(merge_dict2)
        if len(pre_v + pre_g + dom_v) > 0:
            cont = True
            k -= len(dom_v)

    if G["active_nodes"] == 0:
        print('#recursive steps: 0')
        output_VC(v_list, merge_dict)
        return

    md = merge_dict

    to_delete = [x for x in G["vertices"] if not G["vertices"][x]["active"]]
    DESTROY(G, to_delete)

    lp_v_list, lp_g_list = lp_solver2(G)
    v_list += lp_v_list
    DESTROY(G, (lp_v_list + lp_g_list))

    if G["active_nodes"] == 0:
        print('#recursive steps: 0')
        output_VC(v_list, merge_dict)
        return

    unc = unconfined(G)
    k -= len(unc)
    pre_v, pre_g, k, merge_dict2 = preprocess_degree(G, k)
    merge_dict.update(merge_dict2)
    v_list += unc + pre_v
    g_list += pre_g

    if G["active_nodes"] == 0:
        print('#recursive steps: 0')
        output_VC(v_list, merge_dict)
        return

    # delete all unactive vertices before branching
    to_delete = [x for x in G["vertices"] if not G["vertices"][x]["active"]]
    DESTROY(G, to_delete)

    min_k = G["active_nodes"] - len(clique_cover(G))

    G3 = copy.deepcopy(G)
    max_k, upper_bound, merge_dict_heu = heuristic(G3)

    # SEARCH FOR K---------------------------------------------------------------
    if settings.use_constrained_branching:
        print("#start constrained_branching")
        VC, merge_dict2 = constrained_branching(G, [], 0, upper_bound, [])
        keys2 = list(merge_dict2.keys())
        for m in list(merge_dict_heu.keys()):
            if m in keys2:
                merge_dict_heu.pop(m)
        merge_dict_heu.update(merge_dict2)
        merge_dict.update(merge_dict_heu)

    else:  # normal branching
        VC = None
        # binary search for k
        if settings.search_binary:
            k = int((min_k + max_k) / 2)
            while min_k != max_k:
                print("#k =", k)
                G2 = copy.deepcopy(G)
                VC, merge_dict = branch(G2, k)
                if VC is None:
                    min_k = k + 1
                    k = int((k + max_k) / 2)
                else:
                    max_k = k
                    k = int((min_k + k) / 2)

            if VC is None:
                VC, merge_dict = branch(G, min_k)

        # linear search (k+=1)
        if settings.search_linear1:
            k = min_k
            while VC is None:
                graph = copy.deepcopy(G)
                VC, merge_dict = branch(graph, k)
                k += 1

        # linear search (k+=2)
        if settings.search_linear2:
            k = min_k
            while VC is None:
                graph = copy.deepcopy(G)
                VC, merge_dict = branch(graph, k)
                k += 2

            graph = copy.deepcopy(G)
            VC2, merge_dict2 = branch(graph, k - 3)

            if VC2 is not None:
                VC = VC2
                merge_dict = merge_dict2

    # OUTPUT---------------------------------------------------------------------
    if VC is None:
        print("#error")
        return

    VC += v_list

    print('#recursive steps:', settings.recursive_steps)
    print("#|VC| =", len(VC))

    md.update(merge_dict)
    output_VC(VC, md)


settings.init()
main()
