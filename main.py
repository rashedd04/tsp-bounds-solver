import numpy as np
import os
import time
from collections import deque
from tsp_instance import TSPInstance
from tsp_solution import TSPSolution
from scipy.sparse.csgraph import minimum_spanning_tree, maximum_flow
from scipy.sparse import csr_matrix
from scipy.optimize import linprog, linear_sum_assignment
import matplotlib.pyplot as plt
import math

SCIPY_AVAILABLE = True

# UPPER BOUNDS
# UPPER BOUNDS
# UPPER BOUNDS
def solve_nearest_neighbor(instance: TSPInstance) -> TSPSolution:
    start_time = time.time()
    n = instance.n
    visited = {0}
    tour = [0]
    cost = 0.0
    current = 0
    
    while len(visited) < n:
        nearest_dist = float('inf')
        nearest_node = -1
        for next_node in range(n):
            if next_node not in visited:
                d = instance.distance(current, next_node)
                if d < nearest_dist:
                    nearest_dist = d
                    nearest_node = next_node
        
        if nearest_node == -1: break
        visited.add(nearest_node)
        tour.append(nearest_node)
        cost += nearest_dist
        current = nearest_node
    
    if len(visited) == n:
        cost += instance.distance(current, 0)
        
    return TSPSolution(tour=tour, cost=cost, time_seconds=time.time() - start_time)



def solve_nearest_insertion(instance: TSPInstance) -> TSPSolution:
    start_time = time.time()
    n = instance.n
    tour = [0]
    unvisited = list(range(1, n))
    # we start by connecting vertex 0 to the closest one in order to create our first edge
    first_node = min(unvisited, key=lambda k: instance.distance(0, k))
    tour.append(first_node)
    unvisited.remove(first_node)
    
    while unvisited:
        # we search for the closest vertex to our group
        closest_dist = float('inf')
        closest_k = -1
        for k in unvisited:
            for t in tour:
                d = instance.distance(t, k)
                if d < closest_dist:
                    closest_dist = d
                    closest_k = k
        
        # Find the best place to include the closest vertex in our tour
        best_idx = -1
        min_delta = float('inf')
        

        # minimum detour
        for i in range(len(tour)):
            u = tour[i]
            v = tour[(i + 1) % len(tour)]
            delta = instance.distance(u, closest_k) + instance.distance(closest_k, v) - instance.distance(u, v)
            
            if delta < min_delta:
                min_delta = delta
                best_idx = i + 1

        # we insert the vertex and remove it from the unvsited list
        tour.insert(best_idx, closest_k)
        unvisited.remove(closest_k)
        
    cost = sum(instance.distance(tour[i], tour[(i+1)%n]) for i in range(n))
    return TSPSolution(tour=tour, cost=cost, time_seconds=time.time() - start_time)


def apply_2opt(instance: TSPInstance, initial_solution: TSPSolution) -> TSPSolution:
    start_time = time.time()
    # on cree une copie pour laisser l'original
    tour = list(initial_solution.tour)
    best_cost = initial_solution.cost
    improved = True
    n = len(tour)

    # we are switching edges step by step until we find the best pairs( couplage a poids minimum)
    while improved == True:
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n):
                if j - i == 1: continue 
                
                u1, v1 = tour[i-1], tour[i]
                u2, v2 = tour[j], tour[(j+1) % n]
                
                current_dist = instance.distance(u1, v1) + instance.distance(u2, v2)
                new_dist = instance.distance(u1, u2) + instance.distance(v1, v2)
                
                if new_dist < current_dist: 
                    tour[i:j+1] = tour[i:j+1][::-1]
                    best_cost -= (current_dist - new_dist)
                    improved = True 
    actual_final_cost = sum(instance.distance(tour[i], tour[(i+1)%n]) for i in range(n))
    total_time = initial_solution.time_seconds + (time.time() - start_time)
    return TSPSolution(tour=tour, cost=actual_final_cost, time_seconds=initial_solution.time_seconds + (time.time() - start_time))

def solve_spanning_tree_heuristic(instance: TSPInstance) -> TSPSolution:
    #minimum spanning tree heuristic
    if not SCIPY_AVAILABLE: 
        return TSPSolution(cost=float('inf'))
    
    start_time = time.time()
    n = instance.n

    # Minimum Spanning Tree
    matrix = csr_matrix(instance.distances)
    mst_array = minimum_spanning_tree(matrix).toarray()

    # BUILD A NEIGHBOR LIST
    neighbors = [[] for _ in range(n)]
    rows, cols = mst_array.nonzero()
    for i, j in zip(rows, cols):
        neighbors[i].append(j)
        neighbors[j].append(i)

    #If we hit a city we already visited, we go directly to the next new one
    tour = []
    visited = [False] * n
    stack = [0]

    while stack:
        current = stack.pop()
        if not visited[current]:
            visited[current] = True
            tour.append(current)
            for neighbor in neighbors[current]:
                if not visited[neighbor]:
                    stack.append(neighbor)

    cost = sum(instance.distance(tour[i], tour[(i+1)%n]) for i in range(n))
    return TSPSolution(tour=tour, cost=cost, time_seconds=time.time() - start_time)


def apply_tabu_search(instance: TSPInstance, initial_sol: TSPSolution) -> TSPSolution:
    start_time = time.time()
    
    # find our best tour till now
    current_route = list(initial_sol.tour)
    current_cost = initial_sol.cost
    best_route, best_cost = list(current_route), current_cost
    
    # our memory
    tabu_memory = deque(maxlen=10) 
    n = len(current_route)

    for _ in range(50):
        best_move, best_move_cost, move_id = None, float('inf'), None

        # Look at all possible 2-opts
        for i in range(1, n - 2):
            for j in range(i + 1, n):
                if j - i == 1: continue

                # Calculate the cost change
                dist = instance.distance
                change = (dist(current_route[i-1], current_route[j]) + dist(current_route[i], current_route[(j+1)%n])) - \
                         (dist(current_route[i-1], current_route[i]) + dist(current_route[j], current_route[(j+1)%n]))
                
                new_cost = current_cost + change
                this_move = (current_route[i], current_route[j])

                #we choose the best move
                if new_cost < best_move_cost:
                    if this_move not in tabu_memory or new_cost < best_cost:
                        best_move_cost, best_move, move_id = new_cost, (i, j), this_move

        if not best_move: break

        # update our memory
        i, j = best_move
        current_route[i:j+1] = current_route[i:j+1][::-1]
        current_cost = best_move_cost
        tabu_memory.append(move_id)

        # Update our best tour
        if current_cost < best_cost:
            best_cost, best_route = current_cost, list(current_route)
    actual_final_cost = sum(instance.distance(best_route[i], best_route[(i+1)%n]) for i in range(n))
    return TSPSolution(tour=best_route, cost=actual_final_cost, time_seconds=initial_sol.time_seconds + (time.time() - start_time))



# LOWER BOUNDS
# LOWER BOUNDS
# LOWER BOUNDS
# LOWER BOUNDS


def compute_assignment_lb(instance) -> float:
    ## Assigment Problem    
    #we create a matrix of distances then forbid staying in the same city(degin=degout=1) then do a perfect matching
    matrix = instance.distances.copy()
    np.fill_diagonal(matrix, float('inf')) 
    rows, cols = linear_sum_assignment(matrix)
    return matrix[rows, cols].sum()


def compute_1tree_lb(instance):
    n = instance.n
    #build the minimum spanning tree then connecting with city 0 and finally build the full map to be able to visualize it
    sub_matrix = instance.distances[1:, 1:]
    mst_matrix = minimum_spanning_tree(csr_matrix(sub_matrix)).toarray()
    mst_cost = mst_matrix.sum()
    
    dists_to_0 = sorted([(instance.distance(0, i), i) for i in range(1, n)])
    cheapest_1, cheapest_2 = dists_to_0[0], dists_to_0[1]
    
    full_matrix = np.zeros((n, n))
    full_matrix[1:, 1:] = mst_matrix + mst_matrix.T
    full_matrix[0, cheapest_1[1]] = full_matrix[cheapest_1[1], 0] = 1
    full_matrix[0, cheapest_2[1]] = full_matrix[cheapest_2[1], 0] = 1
    
    total_cost = mst_cost + cheapest_1[0] + cheapest_2[0]
    return total_cost, full_matrix



def compute_fractional_2matching_lb(instance) -> float:
    # we will list all the possible roads then making degrees of vertices equal to 2 with fractions if needed and solve with scipy package
    n = instance.n
    
    costs, edge_to_idx = [], {}
    idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            costs.append(instance.distance(i, j))
            edge_to_idx[(i, j)] = idx
            idx += 1
            
    num_edges = len(costs)
    rule_matrix = np.zeros((n, num_edges))
    target_values = np.full(n, 2.0)
    
    for i in range(n):
        for j in range(n):
            if i == j: continue
            e = (i, j) if i < j else (j, i)
            rule_matrix[i, edge_to_idx[e]] = 1.0

    res = linprog(costs, A_eq=rule_matrix, b_eq=target_values, bounds=(0, 1), method='highs')
    return res.fun


def compute_dantzig_cutting_planes_stsp(instance):
    #dantzig for STSP
    n = instance.n
    # we have the same degree = 2 rule and then use maximum flows to test (<2) if there is subtours,
    #  if yes we add cuts to not have these isolated loops and we repeat till we get one single big loop
    # i used scale = 1000 to let the linprog solver of scipy to be able to calculate the decimals instead of rounding 0.5 to 1 or to 0
    costs, edge_to_idx, idx_to_edge = [], {}, {}
    idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            costs.append(instance.distance(i, j))
            edge_to_idx[(i, j)] = idx
            idx_to_edge[idx] = (i, j)
            idx += 1
            
    num_edges = len(costs)
    rule_matrix = np.zeros((n, num_edges))
    target_values = np.full(n, 2.0)
    for i in range(n):
        for j in range(n):
            if i == j: continue
            e = (i, j) if i < j else (j, i)
            rule_matrix[i, edge_to_idx[e]] = 1.0

    subtour_rules, subtour_targets = [], []
    best_cost = 0.0
    final_graph = np.zeros((n, n))
    SCALE = 1000
    for iteration in range(100): 
        res = linprog(costs, A_eq=rule_matrix, b_eq=target_values, 
                      A_ub=np.array(subtour_rules) if subtour_rules else None, 
                      b_ub=np.array(subtour_targets) if subtour_targets else None, 
                      bounds=(0, 1), method='highs')
        if not res.success: break
        
        best_cost = res.fun
        
        capacity_matrix = np.zeros((n, n))
        for i in range(num_edges):
            if res.x[i] > 1e-4:
                u, v = idx_to_edge[i]
                capacity_matrix[u, v] = capacity_matrix[v, u] = res.x[i]
                
        final_graph = capacity_matrix
        int_capacity_matrix = (capacity_matrix * 1000).astype(np.int32)
        graph = csr_matrix(int_capacity_matrix)

        violated_cut_found = False
        source = 0
        for sink in range(1, n):
            flow_result = maximum_flow(graph, source, sink)
            
            if flow_result.flow_value < (1.99 * SCALE): 
                flow_matrix = flow_result.flow.toarray()
                residual = int_capacity_matrix - flow_matrix + flow_matrix.T
                
                visited = np.zeros(n, dtype=bool)
                queue = [source]
                visited[source] = True
                while queue:
                    u = queue.pop(0)
                    for v in range(n):
                        if not visited[v] and residual[u, v] > 0:
                            visited[v] = True
                            queue.append(v)
                            
                island_nodes = np.where(visited)[0]
                if 1 < len(island_nodes) < n:
                    new_rule = np.zeros(num_edges)
                    for idx_e, (u, v) in idx_to_edge.items():
                        if u in island_nodes and v in island_nodes:
                            new_rule[idx_e] = 1.0
                            
                    subtour_rules.append(new_rule)
                    subtour_targets.append(len(island_nodes) - 1.0)
                    violated_cut_found = True
                    break 
                    
        if not violated_cut_found: break

    return best_cost, final_graph


def compute_dantzig_cutting_planes_atsp(instance):
    #dantzig for ATSP
    n = instance.n
    # we force every vertex to only have 1 degin and 1 degout then we use the maximum flow to test for subtours, we test the flow in both directions
    #  (in and out) then we add the cuts to ban the isolated subtours and we repeat until having one single loop
    #we used the same scale like the STSP
    
    costs, edge_to_idx, idx_to_edge = [], {}, {}
    idx = 0
    for i in range(n):
        for j in range(n):
            if i == j: continue
            costs.append(instance.distance(i, j))
            edge_to_idx[(i, j)] = idx
            idx_to_edge[idx] = (i, j)
            idx += 1
            
    num_edges = len(costs)
    
    rule_matrix = np.zeros((2 * n, num_edges))
    target_values = np.ones(2 * n)
    for i in range(n):
        for j in range(n):
            if i == j: continue
            e_idx = edge_to_idx[(i, j)]
            rule_matrix[i, e_idx] = 1.0          
            rule_matrix[n + j, e_idx] = 1.0      

    subtour_rules, subtour_targets = [], []
    best_cost = 0.0
    final_graph = np.zeros((n, n))
    SCALE = 1000
    for iteration in range(100): 
        res = linprog(costs, A_eq=rule_matrix, b_eq=target_values, 
                      A_ub=np.array(subtour_rules) if subtour_rules else None, 
                      b_ub=np.array(subtour_targets) if subtour_targets else None, 
                      bounds=(0, 1), method='highs')
        if not res.success: break
        
        best_cost = res.fun
        capacity_matrix = np.zeros((n, n))
        for i in range(num_edges):
            if res.x[i] > 1e-4:
                u, v = idx_to_edge[i]
                capacity_matrix[u, v] = res.x[i] 
                
        final_graph = capacity_matrix
        int_capacity_matrix = (capacity_matrix * SCALE).astype(np.int32)
        graph = csr_matrix(int_capacity_matrix)
        violated_cut_found = False
        
        for t in range(1, n):
            flow_result = maximum_flow(graph, 0, t)
            
            if flow_result.flow_value < int(0.99 * SCALE):
                flow_matrix = flow_result.flow.toarray()
                residual = int_capacity_matrix - flow_matrix + flow_matrix.T
                
                visited = np.zeros(n, dtype=bool)
                queue = [0]
                visited[0] = True
                while queue:
                    u = queue.pop(0)
                    for v in range(n):
                        if not visited[v] and residual[u, v] > 0:
                            visited[v] = True
                            queue.append(v)
                            
                island_nodes = np.where(visited)[0]
                if 1 < len(island_nodes) < n:
                    new_rule = np.zeros(num_edges)
                    for idx_e, (u, v) in idx_to_edge.items():
                        if u in island_nodes and v in island_nodes:
                            new_rule[idx_e] = 1.0
                    subtour_rules.append(new_rule)
                    subtour_targets.append(len(island_nodes) - 1.0)
                    violated_cut_found = True
                    break
        if not violated_cut_found: break

    return best_cost, final_graph


def compute_lagrangian_lb_stsp(instance, best_ub: float) -> float:
    #Lagrangian relaxation
    n=instance.n
    # we start by putting penalties to 0 then we define epilon = 2 which 
    # is the maximum and the reduction will be 0.95 so each time we reduce by
    #  5% and for 300 times we create the matrix of the penalties then we 
    # calculate the 1-Tree with these new costs and then add the constant 2* sum of u_i
    #  then we calculate degrees then raise penalties on vertices with high degrees to avoid them 
    # and vuce versa and in each iteration we reduce the penalties that we add which maximized our lower bound
    u = np.zeros(n)
    best_lb = 0.0
    epsilon = 2.0  
    rho = 0.95     
    
    for iteration in range(300): 
        w = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                w[i, j] = instance.distance(i, j) - u[i] - u[j]
                w[j, i] = w[i, j]
                
        sub_w = w[1:, 1:]
        mst_matrix = minimum_spanning_tree(csr_matrix(sub_w)).toarray()
        
        dists_to_0 = [(w[0, i], i) for i in range(1, n)]
        dists_to_0.sort()
        tree_weight = mst_matrix.sum() + dists_to_0[0][0] + dists_to_0[1][0]
        lagrangian_cost = tree_weight + 2 * np.sum(u)
        
        if lagrangian_cost > best_lb:
            best_lb = lagrangian_cost
            
        degrees = np.zeros(n)
        rows, cols = mst_matrix.nonzero()
        for r, c in zip(rows, cols):
            degrees[r + 1] += 1
            degrees[c + 1] += 1
            
        degrees[0] = 2
        degrees[dists_to_0[0][1]] += 1
        degrees[dists_to_0[1][1]] += 1
        subgradient = 2.0 - degrees
        
        sum_sq_grad = np.sum(subgradient ** 2)
        if sum_sq_grad == 0:
            best_lb = lagrangian_cost
            break 
            
        step_size = epsilon * (best_ub - lagrangian_cost) / sum_sq_grad
        u = u + step_size * subgradient        
        epsilon *= rho

    return best_lb

def main():
    # Repo packaging: instances live in ./instances (added when the project was moved to its own repo)
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "instances"))
    # partie affichage cree par un ia pour afficher des belles tableaus facile a lire
    #prompt utilisé: i want a main block to test all my files and use the functions above in order
    #  to get all the solutions , costs, time of processing and put them in nice organized tables 
    # with instance name, type(stsp or atsp) , time of execution and cost for both upper and lower bounds
    files_to_test = [
        "instance_8nodes.tsp",
        "warehouse_5v_10p.tsp", 
        "warehouse_10v_30p.tsp", 
        "warehouse_10v_50p.tsp",
        "bays29.tsp",
        "dantzig42.tsp",
        "pr76.tsp",
        "ftv33.atsp",
        "p43.atsp",
        "ftv70.atsp"
    ]

    all_results = []

    print("Calcul de TOUTES les méthodes en cours... Patience !\n")

    for filename in files_to_test:
        if not os.path.exists(filename): 
            print(f"Fichier introuvable : {filename}")
            continue
            
        instance = TSPInstance.from_tsplib(filename)
        is_atsp = filename.endswith(".atsp")
        type_str = "ATSP" if is_atsp else "STSP"
        
        # --- 1. UPPER BOUNDS ---
        sol_nn = solve_nearest_neighbor(instance)
        sol_ni = solve_nearest_insertion(instance)
        sol_sth = solve_spanning_tree_heuristic(instance)
        
        if is_atsp:
            sol_nn_2opt = TSPSolution(tour=[], cost=float('inf'), time_seconds=0.0)
            sol_ni_2opt = TSPSolution(tour=[], cost=float('inf'), time_seconds=0.0)
            sol_nn_tabu = TSPSolution(tour=[], cost=float('inf'), time_seconds=0.0)
        else:
            sol_nn_2opt = apply_2opt(instance, sol_nn)
            sol_ni_2opt = apply_2opt(instance, sol_ni)
            sol_nn_tabu = apply_tabu_search(instance, sol_nn)
            
        # --- 2. LOWER BOUNDS ---
        # A. Assignment Problem (AP)
        t0 = time.time()
        lb_ap_val = compute_assignment_lb(instance)
        t_ap = time.time() - t0
        
        # B. 1-Tree & Lagrangien (STSP Uniquement)
        if is_atsp:
            lb_1t_val, t_1t = float('inf'), 0.0
            lb_lagr_val, t_lagr = float('inf'), 0.0
        else:
            # 1-Tree classique
            t0 = time.time()
            lb_1t_val = compute_1tree_lb(instance)[0]
            t_1t = time.time() - t0
            
            # Lagrangien (utilise la meilleure borne supérieure trouvée)
            t0 = time.time()
            best_ub = min(sol_nn_tabu.cost, sol_ni_2opt.cost)
            lb_lagr_val = compute_lagrangian_lb_stsp(instance, best_ub)
            t_lagr = time.time() - t0
            
        # C. Dantzig LP
        t0 = time.time()
        if is_atsp:
            lb_dantz_val = compute_dantzig_cutting_planes_atsp(instance)[0]
        else:
            lb_dantz_val = compute_dantzig_cutting_planes_stsp(instance)[0]
        t_dantz = time.time() - t0
        
        # --- 3. SAUVEGARDE DES RÉSULTATS ---
        all_results.append({
            "name": instance.name,
            "type": type_str,
            "c_nn": f"{sol_nn.cost:.1f}",
            "c_ni": f"{sol_ni.cost:.1f}",
            "c_sth": f"{sol_sth.cost:.1f}",
            "c_nn2": f"{sol_nn_2opt.cost:.1f}" if not is_atsp else "N/A",
            "c_ni2": f"{sol_ni_2opt.cost:.1f}" if not is_atsp else "N/A",
            "c_tabu": f"{sol_nn_tabu.cost:.1f}" if not is_atsp else "N/A",
            "t_nn": f"{sol_nn.time_seconds:.3f}s",
            "t_ni": f"{sol_ni.time_seconds:.3f}s",
            "t_sth": f"{sol_sth.time_seconds:.3f}s",
            "t_nn2": f"{sol_nn_2opt.time_seconds:.3f}s" if not is_atsp else "N/A",
            "t_ni2": f"{sol_ni_2opt.time_seconds:.3f}s" if not is_atsp else "N/A",
            "t_tabu": f"{sol_nn_tabu.time_seconds:.3f}s" if not is_atsp else "N/A",
            "c_ap": f"{lb_ap_val:.1f}",
            "c_1t": f"{lb_1t_val:.1f}" if not is_atsp else "N/A",
            "c_lagr": f"{lb_lagr_val:.1f}" if not is_atsp else "N/A",  # NOUVEAU
            "c_dantz": f"{lb_dantz_val:.1f}",
            "t_ap": f"{t_ap:.3f}s",
            "t_1t": f"{t_1t:.3f}s" if not is_atsp else "N/A",
            "t_lagr": f"{t_lagr:.3f}s" if not is_atsp else "N/A",      # NOUVEAU
            "t_dantz": f"{t_dantz:.3f}s"
        })

    # --- 4. AFFICHAGE DES TABLEAUX ---
    sep_ub = "-" * 85
    sep_lb = "-" * 80  # Élargi pour la nouvelle colonne

    print("\n" + sep_ub)
    print("TABLE 1: UPPER BOUNDS (COÛTS)")
    print(f"{'Instance':<15} {'Type':<5} | {'NN':<8} {'NI':<8} {'ST-Heur':<8} | {'NN+2Opt':<9} {'NI+2Opt':<9} {'NN+Tabu':<9}")
    print(sep_ub)
    for r in all_results:
        print(f"{r['name']:<15} {r['type']:<5} | {r['c_nn']:<8} {r['c_ni']:<8} {r['c_sth']:<8} | {r['c_nn2']:<9} {r['c_ni2']:<9} {r['c_tabu']:<9}")
        
    print("\n" + sep_ub)
    print("TABLE 2: UPPER BOUNDS (TEMPS D'EXÉCUTION)")
    print(f"{'Instance':<15} {'Type':<5} | {'NN':<8} {'NI':<8} {'ST-Heur':<8} | {'NN+2Opt':<9} {'NI+2Opt':<9} {'NN+Tabu':<9}")
    print(sep_ub)
    for r in all_results:
        print(f"{r['name']:<15} {r['type']:<5} | {r['t_nn']:<8} {r['t_ni']:<8} {r['t_sth']:<8} | {r['t_nn2']:<9} {r['t_ni2']:<9} {r['t_tabu']:<9}")

    print("\n" + sep_lb)
    print("TABLE 3: LOWER BOUNDS (COÛTS)")
    print(f"{'Instance':<15} {'Type':<5} | {'Assign(AP)':<12} {'1-Tree':<10} {'Lagrangien':<12} {'Dantzig_LP':<10}")
    print(sep_lb)
    for r in all_results:
        print(f"{r['name']:<15} {r['type']:<5} | {r['c_ap']:<12} {r['c_1t']:<10} {r['c_lagr']:<12} {r['c_dantz']:<10}")

    print("\n" + sep_lb)
    print("TABLE 4: LOWER BOUNDS (TEMPS D'EXÉCUTION)")
    print(f"{'Instance':<15} {'Type':<5} | {'Assign(AP)':<12} {'1-Tree':<10} {'Lagrangien':<12} {'Dantzig_LP':<10}")
    print(sep_lb)
    for r in all_results:
        print(f"{r['name']:<15} {r['type']:<5} | {r['t_ap']:<12} {r['t_1t']:<10} {r['t_lagr']:<12} {r['t_dantz']:<10}")
    print(sep_lb + "\n")

if __name__ == "__main__":
    main()