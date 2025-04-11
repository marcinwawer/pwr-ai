import heapq, time
from src.Config.constants import MIN_CHANGE_TIME, TIME_COST_PER_SEC



def dijkstra_min_time(graph, start_stop, end_stop, start_time):
    t0 = time.time()  
    best_arrival = {start_stop: start_time}
    queue = []
    heapq.heappush(queue, (start_time, start_stop, []))
    
    while queue:
        current_time, current_stop, path = heapq.heappop(queue)

        if current_stop == end_stop:
            run_time = time.time() - t0  
            return (current_time - start_time).total_seconds() * TIME_COST_PER_SEC, path, run_time
        
        if current_stop not in graph:
            continue

        for conn in graph[current_stop]:
            if conn['departure_time'] >= current_time:
                if path:
                    last_line = path[-1]['line']
                    if last_line != conn['line']:
                        wait_time = conn['departure_time'] - current_time
                        if wait_time < MIN_CHANGE_TIME:
                            continue

                arrival = conn['arrival_time']

                if conn['end_stop'] in best_arrival and arrival >= best_arrival[conn['end_stop']]:
                    continue

                best_arrival[conn['end_stop']] = arrival
                new_path = path + [conn]
                heapq.heappush(queue, (arrival, conn['end_stop'], new_path))

    run_time = time.time() - t0
    return None, None, run_time