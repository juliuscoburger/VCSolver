from helps import activeVertices


def clique_cover(graph: dict, neighbors=None) -> list:
    """
    Neighbors are only set if needed, if set, 
    then only compute the clique cover of neighbors.
    
    :param graph:
    :param neighbors:
    :return: return list of cliques
    """
    cliques = []
    inserted = []

    if neighbors is None:
        to_analyze = activeVertices(graph)
    else:
        to_analyze = neighbors

    for v in to_analyze:
        for c in cliques:
            if set(c).issubset(set(graph["vertices"][v]["neighbors"])):
                c.append(v)
                inserted.append(v)
                break

        if v not in inserted:
            cliques.append([v])

    return cliques
