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

### Data reduction rules

Data reduction rules serve the purpose of reducing the input graph by taking "obvious" nodes into the solution.  This makes the graph smaller and the whole algorithm faster. Although the reduction rules give improvement, the overall runningtime is unchanged.

Implemented data reduction rules:
- Delete Deg-0 vertices
- Process Deg-1 and Deg-2 vertices
- Take vertices with Deg-k into the VC, if k is greater than the VC
- Domination rule
- Finding Unconfied vertices
- Deg-3 Independet Set rule
- Crown rule
- Linear Program


### Branching

Instead of checking for each vertex if it belongs in the VC or not and trying all possibilities recursivly. I take a node <img src="https://render.githubusercontent.com/render/math?math=v \in V"> and either take v into VC or take all the neighbors <img src="https://render.githubusercontent.com/render/math?math=\mathcal{N}(v)"> of v into VC. This improves the branching and thus reduces the running time to ![My Formula](https://latex.codecogs.com/gif.latex?O(n^2(m+{1.47}^k))).



## Input/Output

The input is passed to the programm via stdin. Input edge after edge. Inputfiles can be seen in the file "instances".

Run with:
```python3 VC.py < instances/instance1.input```


Further settings can be inputted in the commandline:
```
ARGS:
    [0] - frequency of datasreduction rules by recursive depth ("True") or by recursive steps ("False")
    
    [1] - search method: either binary search ("sb"), two forms of linear search("sl1" and "sl2") or constrianed branching (anything else as argument)
    
    [2] to [6] - settings on how often to use the following datareduction rules: domination rule, crown rule, LP, unconfined vertices, a second preprocessing - arguement is an integer and specifies the frequency
    
    [7] - aplly LP exhaustivly - either True or False
    
    [8] to [10] - settings on how often to use the following datareduction rules: two-clique rule, two clique degree, degree-3-intependent set rule - - arguement is an integer and specifies the frequency
    
    
    python3 VC.py True sb 1 1 1 1 1 True 1 1 1 < instances/instance1.input # Every rule is applied at every branching step. (Although there is no branching for instance1 and it is soley solved using preprocessing and datareduction rules)
    



```





