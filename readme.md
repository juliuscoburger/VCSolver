#Vertex Cover Solver

A vertex cover VC of an undirected graph G = (V,E) is a subset of V such that each edge has at least one endpoint in VC. The problem is to find smallest VC possible. 

Finding the smallest Vertex Cover is an NP-hard problems. Since the Question "P=NP?" is still unanswered, it is still unknown if a polynominal-time algorithm solving this problems exists.
The most trivial algorithm to solve the problem is a simple brute-force algorithm in O(2^n) running time dependent on the number of nodes n. 

With different data reduction rules and branching strategies the running time can be drastically reduced.
