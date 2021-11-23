from helps import read_edges
from matching import matching


def flow(G):
    """
    :param G:
    :return:
    """
    M = matching(G)

    E = []
    for key, value in M.items():
        E.append([key, value])
    A = list(set([v for e in E for v in e]))
    B = [v for v in list(G["vertices"]) if v not in A]
    EAB = [[u, v] for u in A for v in B]
    GAB = read_edges(EAB)  # bipartite graph
    M2 = matching(GAB)
    match = list(M2)
    EAB2 = [v for v in EAB if v not in match]

    GAB2 = read_edges(EAB2)
    U = [v for v in GAB["vertices"] if v not in match]

    Z = []
    Q = [[u, 0] for u in U]

    visited = []

    while len(Q) != 0:
        v = Q[0]
        if v[0] in visited:
            Q.remove(v)
            continue
        visited.append(v[0])
        Z.append(v[0])
        if v[1] % 2 == 1:
            neigh = [[M2[v[0]], v[1] + 1]]
        else:
            neigh = [[n, v[1] + 1] for n in GAB2["vertices"][v[0]]["neighbors"]]
        Q.extend(neigh)
        Q.remove(v)

    K = [v for v in A if v not in Z] + [v for v in B if v in Z]

    if len(M2) == 0:
        K = []

    AX = [x for x in K if x in A]
    B0 = [x for x in B if x not in K]

    if len(K) != int(len(M2) / 2):
        print("mistake")

    return AX, B0, M
