from helps import activeVertices


#neighbors is only set when needed
#if neighbors is set, then only compute cc of neighbors
def clique_cover(G, neighbors=None):
    cliques = []
    inserted = []

    if neighbors == None:
        to_analyze = activeVertices(G)
    else:
        to_analyze = neighbors

    for v in to_analyze:
        for c in cliques:
            if set(c).issubset(set(G["vertices"][v]["neighbors"])):
                c.append(v)
                inserted.append(v)
                break

        if v not in inserted:
            cliques.append([v])

    return cliques
