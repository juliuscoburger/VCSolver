def init():
    
    #Count recursive steps
    global recursive_steps

    #apply rule while branching
    global branch_domination
    global branch_crowns
    global branch_lp
    global branch_unconfined
    global branch_second_prep
    global branch_lp_exhaustivly
    global branch_two_clique
    global branch_two_clique_degree #only inspect for vertices with smaller degree
    global branch_deg_3_independent
    
    #search k strategy
    global use_constrained_branching
    global search_binary
    global search_linear1 #inkrement by 1
    global search_linear2 #inkrement by 2
    
    #frequency parameter
    global freq_by_rec_steps 
    global freq_by_rec_depth
    
    
    #Set Values-------------------------------------------------
    recursive_steps = 0

    branch_domination           = 4
    branch_crowns               = 5
    branch_lp                   = 20
    branch_unconfined           = 10
    branch_second_prep          = 1
    branch_lp_exhaustivly       = False
    branch_two_clique           = 3
    branch_two_clique_degree    = 50
    branch_deg_3_independent    = 3
    
    use_constrained_branching   = True    
    search_binary               = False  
    search_linear1              = False     
    search_linear2              = False      
    
    freq_by_rec_steps           = True
    freq_by_rec_depth           = False
    
