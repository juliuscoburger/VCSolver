# Vertex Cover Solver

A vertex cover VC of an undirected graph G = (V,E) is a subset of V such that each edge has at least one endpoint in VC. The problem is to find smallest VC possible. 

Finding the smallest Vertex Cover is an NP-hard problems. Since the Question "P=NP?" is still unanswered, it is still unknown if a polynominal-time algorithm solving this problems exists.
The most trivial algorithm to solve the problem is a simple brute-force algorithm in <img src="https://render.githubusercontent.com/render/math?math=O(2^n)"> running time dependent on the number of nodes n. 

With different data reduction rules and branching strategies the running time can be drastically reduced.

## Trivial solution

```{r, tidy=FALSE, eval=FALSE, highlight=FALSE }

def find_smallest_VC(G):
    VC = None
    n = 1
    while VC==None:
        VC = find_VC(G,n) #checks for VC of size n in G
        n += 1
  
   print(VC)
   return
  

def find_VC(G, n):
    if n==0:
        return None

    e1, e2 = get_edge(G)  #retruns random edge with endnodes e1,e2 in G
    
    VC1 = find_VC(G\e1, n-1)  # G\e1 deletes node e1 from G
    VC2 = find_VC(G\e2, n-1)
    
    
    if VC1 == None:
        return VC2
    return VC1
```

The function find_smallest_VC() linearly searches for the smallest n by trying all solutions using the recursive find_VC() function. The running time is  <img src="https://render.githubusercontent.com/render/math?math=O(2^n)">.

## Improvements


### Branching


### Data reduction rules




## Input/Output

The input is passed to the programm via stdin. Input edge after edge. Inputfiles can be seen in the file "instances"

