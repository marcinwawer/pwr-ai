import random
import time
from src.Config.constants import MIN_CHANGE_TIME, CHANGE_COST_PER_CHANGE, TIME_COST_PER_SEC
from collections import deque



def calculate_route_cost(initial_time, start_stop, route, graph, cost_func, criterion):
    total_cost = 0.0
    segments = []
    current_stop = start_stop
    current_time = initial_time
    previous_line = None  

    for next_stop in route + [start_stop]:
        segment_cost, segment_path, _ = cost_func(graph, current_stop, next_stop, current_time)

        if segment_cost is None or segment_path is None or len(segment_path) == 0:
            return float('inf'), None

        current_segment_line = segment_path[0]['line']

        if previous_line is not None and current_segment_line != previous_line:
            wait_time = (segment_path[0]['departure_time'] - current_time).total_seconds()
            
            if wait_time < MIN_CHANGE_TIME.total_seconds():
                return float('inf'), None
            
            change_cost = CHANGE_COST_PER_CHANGE
        else:
            change_cost = 0

        if criterion in ["time", "t"]:
            total_cost += segment_cost
        elif criterion in ["change", "c"]:
            total_cost += change_cost + segment_cost

        segments.append((current_stop, next_stop, segment_path))
        current_time = segment_path[-1]['arrival_time']
        previous_line = segment_path[-1]['line']
        current_stop = next_stop

    return total_cost, segments



def tabu_search_route(start_stop, stops, initial_time, graph, cost_func, criterion, iterations=1000):
    t0 = time.time()

    if criterion not in ["time", "t", "change", "c"]:
        raise ValueError("wrong criterion")
    
    current_solution = stops[:]
    random.shuffle(current_solution)
    
    best_cost, best_segments = calculate_route_cost(initial_time, start_stop, current_solution, graph, cost_func, criterion)
    best_solution = current_solution[:]
    tabu_list = set()

    for it in range(iterations):
        neighborhood = []
        n = len(current_solution)

        for i in range(n):
            for j in range(i + 1, n):
                neighbor = current_solution[:]
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                move = (i, j)
                if move in tabu_list:
                    continue
                cost, segments = calculate_route_cost(initial_time, start_stop, neighbor, graph, cost_func, criterion)
                neighborhood.append((cost, neighbor, segments, move))
        
        if not neighborhood:
            break
        
        neighborhood.sort(key=lambda x: x[0])
        best_neighbor_cost, best_neighbor, best_neighbor_segments, best_move = neighborhood[0]
        current_solution = best_neighbor
        tabu_list.add(best_move)
        
        if best_neighbor_cost < best_cost:
            best_cost = best_neighbor_cost
            best_solution = best_neighbor[:]
            best_segments = best_neighbor_segments

    run_time = time.time() - t0 
    return best_cost, best_solution, best_segments, run_time



def tabu_search_route_dynamic_size(start_stop, stops, initial_time, graph, cost_func, criterion, iterations=1000):
    t0 = time.time()

    max_tabu_size = len(stops) * 2  
    tabu_list = deque(maxlen=max_tabu_size)

    current_solution = stops[:]
    random.shuffle(current_solution)
    
    best_cost, best_segments = calculate_route_cost(initial_time, start_stop, current_solution, graph, cost_func, criterion)
    best_solution = current_solution[:]

    for it in range(iterations):
        neighborhood = []
        n = len(current_solution)

        for i in range(n):
            for j in range(i + 1, n):
                neighbor = current_solution[:]
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                move = (i, j)

                if move in tabu_list:
                    continue

                cost, segments = calculate_route_cost(initial_time, start_stop, neighbor, graph, cost_func, criterion)
                neighborhood.append((cost, neighbor, segments, move))
        
        if not neighborhood:
            break
        
        neighborhood.sort(key=lambda x: x[0])
        best_neighbor_cost, best_neighbor, best_neighbor_segments, best_move = neighborhood[0]
        current_solution = best_neighbor
        tabu_list.append(best_move) 
        
        if best_neighbor_cost < best_cost:
            best_cost = best_neighbor_cost
            best_solution = best_neighbor[:]
            best_segments = best_neighbor_segments

    run_time = time.time() - t0 
    return best_cost, best_solution, best_segments, run_time



def tabu_search_route_aspiration_rule(start_stop, stops, initial_time, graph, cost_func, criterion, iterations=1000):
    t0 = time.time()

    if criterion not in ["time", "t", "change", "c"]:
        raise ValueError("wrong criterion")
    
    current_solution = stops[:]
    random.shuffle(current_solution)
    
    best_cost, best_segments = calculate_route_cost(initial_time, start_stop, current_solution, graph, cost_func, criterion)
    best_solution = current_solution[:]
    tabu_list = set()

    for it in range(iterations):
        neighborhood = []
        n = len(current_solution)

        for i in range(n):
            for j in range(i + 1, n):
                neighbor = current_solution[:]
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                move = (i, j)
                cost, segments = calculate_route_cost(initial_time, start_stop, neighbor, graph, cost_func, criterion)
                
                if move in tabu_list and cost >= best_cost:
                    continue

                neighborhood.append((cost, neighbor, segments, move))
        
        if not neighborhood:
            break
        
        neighborhood.sort(key=lambda x: x[0])
        best_neighbor_cost, best_neighbor, best_neighbor_segments, best_move = neighborhood[0]
        current_solution = best_neighbor
        tabu_list.add(best_move)
        
        if best_neighbor_cost < best_cost:
            best_cost = best_neighbor_cost
            best_solution = best_neighbor[:]
            best_segments = best_neighbor_segments

    run_time = time.time() - t0 
    return best_cost, best_solution, best_segments, run_time



def tabu_search_route_with_sampling(start_stop, stops, initial_time, graph, cost_func, criterion, iterations=1000, sample_ratio=0.5):
    t0 = time.time()
    
    if criterion not in ["time", "t", "change", "c"]:
        raise ValueError("wrong criterion")
    
    current_solution = stops[:]
    random.shuffle(current_solution)
    
    best_cost, best_segments = calculate_route_cost(initial_time, start_stop, current_solution, graph, cost_func, criterion)
    best_solution = current_solution[:]
    
    tabu_list = set()
    
    n = len(current_solution)
    all_moves = [(i, j) for i in range(n) for j in range(i+1, n)]
    sample_size = max(1, int(len(all_moves) * sample_ratio))
    
    for it in range(iterations):
        neighborhood = []
        sampled_moves = random.sample(all_moves, sample_size)
        
        for move in sampled_moves:
            i, j = move
            neighbor = current_solution[:]
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            cost, segments = calculate_route_cost(initial_time, start_stop, neighbor, graph, cost_func, criterion)

            if move in tabu_list and cost >= best_cost:
                continue

            neighborhood.append((cost, neighbor, segments, move))
        
        if not neighborhood:
            break

        neighborhood.sort(key=lambda x: x[0])
        best_neighbor_cost, best_neighbor, best_neighbor_segments, best_move = neighborhood[0]
        current_solution = best_neighbor
        tabu_list.add(best_move)
        if best_neighbor_cost < best_cost:
            best_cost = best_neighbor_cost
            best_solution = best_neighbor[:]
            best_segments = best_neighbor_segments

    run_time = time.time() - t0
    return best_cost, best_solution, best_segments, run_time