"""
Heuristics are a great way to quickly compute a rough upper bound on the minimal vertex cover of a graph.
This upper bound can be used in to restrict the branching.

Computing the heuristic must be computational easy.
"""
from helps import delete_vertices, get_active_neighbors, activeVertices, DESTROY
from preprocess import preprocess_degree


def heuristic1(graph: dict) -> list:
    """
    :param graph: graph to compute the heuristic for
    :return: list of nodes to take
    """
    max_d = 0
    max_v = []
    for v in activeVertices(graph):
        deg = graph["vertices"][v]["active_degree"]
        if deg > max_d:
            max_d = deg
            max_v = [v]
        elif deg == max_d and deg != 0:
            max_v.append(v)
    delete_vertices(graph, max_v)
    return max_v


def heuristic3(graph: dict):
    """
    :param graph: graph to compute the heuristic for
    :return:
    """
    v_list = []
    for v in graph["vertices"]:
        if graph["vertices"][v]["active"]:
            if graph["vertices"][v]["active_degree"] > 6:
                v_list += [v]
                delete_vertices(graph, [v])
    v1, md = recursive_preprocessing(graph, graph["active_nodes"] - 1)
    v_list += v1
    for v in graph["vertices"]:
        if graph["vertices"][v]["active"]:
            if graph["vertices"][v]["active_degree"] <= 3:
                neig = get_active_neighbors(graph, v)
                v_list += neig
                delete_vertices(graph, neig)
    return v_list, md


def heuristic(graph: dict):
    """
    :param graph: graph to compute the heuristic for
    :return:
    """
    v_list, merge_dict = heuristic3(graph)
    while graph["active_nodes"] > 0:
        DESTROY(graph, [x for x in graph["vertices"] if not graph["vertices"][x]["active"]])
        v_list2, merge_dict2 = recursive_preprocessing(graph, graph["active_nodes"] - 1)
        v_list += v_list2
        merge_dict.update(merge_dict2)
        if graph["active_nodes"] == 0:
            break
        v_list += heuristic1(graph)

    return len(v_list), v_list, merge_dict


def recursive_preprocessing(graph: dict, k):
    v_list = []
    merge_dict = {}
    cont = True
    while cont:
        cont = False
        pre_v, _, _, md = preprocess_degree(graph, k)
        v_list += pre_v
        merge_dict.update(md)
        if len(pre_v) > 0:
            cont = True
    return v_list, merge_dict
