import csv, heapq, math, time
from src.Config.constants import FILE_NAME, TIME_COST_PER_SEC, CHANGE_COST_PER_CHANGE, MIN_CHANGE_TIME



def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c



def load_stop_coords():
    stop_coords = {}
    with open(FILE_NAME, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                lat_start = float(row['start_stop_lat'])
                lon_start = float(row['start_stop_lon'])
                lat_end = float(row['end_stop_lat'])
                lon_end = float(row['end_stop_lon'])
            except Exception as e:
                continue

            if row['start_stop'] not in stop_coords:
                stop_coords[row['start_stop']] = (lat_start, lon_start)

            if row['end_stop'] not in stop_coords:
                stop_coords[row['end_stop']] = (lat_end, lon_end)

    return stop_coords



def a_star_min_time(graph, stop_coords, start_stop, end_stop, start_time, max_speed=15):
    t0 = time.time() 

    if start_stop not in stop_coords or end_stop not in stop_coords:
        print("no coordinates for one or more stops")
        run_time = time.time() - t0  
        return None, None, run_time
    
    dest_lat, dest_lon = stop_coords[end_stop]

    def heuristic(stop):
        if stop in stop_coords:
            lat, lon = stop_coords[stop]
            distance = haversine(lat, lon, dest_lat, dest_lon)
            return distance / max_speed 
        return 0

    open_set = []
    start_h = heuristic(start_stop)
    heapq.heappush(open_set, (start_h, 0, start_stop, start_time, []))
    best_g = {start_stop: 0}
    
    while open_set:
        f, g, current_stop, current_time, path = heapq.heappop(open_set)

        if current_stop == end_stop:
            run_time = time.time() - t0  
            return g, path, run_time
        
        if current_stop not in graph:
            continue

        for conn in graph[current_stop]:
            if conn['departure_time'] >= current_time:
                if path:
                    last_line = path[-1]['line']
                    if last_line != conn['line']:
                        wait_delta = conn['departure_time'] - current_time
                        if wait_delta < MIN_CHANGE_TIME:
                            continue

                wait_time = (conn['departure_time'] - current_time).total_seconds()
                travel_time = (conn['arrival_time'] - conn['departure_time']).total_seconds()
                new_g = g + ((wait_time + travel_time) * TIME_COST_PER_SEC)
                new_stop = conn['end_stop']
                new_time = conn['arrival_time']

                if new_stop in best_g and new_g >= best_g[new_stop]:
                    continue

                best_g[new_stop] = new_g
                h = heuristic(new_stop)
                new_f = new_g + h
                new_path = path + [conn]
                heapq.heappush(open_set, (new_f, new_g, new_stop, new_time, new_path))

    run_time = time.time() - t0  
    return None, None, run_time



def a_star_min_changes(graph, start_stop, end_stop, start_time):
    t0 = time.time()

    open_set = []
    heapq.heappush(open_set, (0, 0, start_stop, start_time, None, []))
    best = {}  

    while open_set:
        f, g, current_stop, current_time, current_line, path = heapq.heappop(open_set)

        if current_stop == end_stop:
            run_time = time.time() - t0
            return g, path, run_time
        
        if current_stop not in graph:
            continue

        for conn in graph[current_stop]:
            if conn['departure_time'] >= current_time:
                new_line = conn['line']
                new_changes = g

                if current_line is not None and new_line != current_line:
                    wait_time = conn['departure_time'] - current_time
                    if wait_time < MIN_CHANGE_TIME:
                        continue 
                    new_changes += CHANGE_COST_PER_CHANGE
                
                new_time = conn['arrival_time']
                state = (conn['end_stop'], new_line)

                if state in best:
                    best_changes, best_time = best[state]
                    if new_changes > best_changes or (new_changes == best_changes and new_time >= best_time):
                        continue

                best[state] = (new_changes, new_time)
                new_f = new_changes  
                new_path = path + [conn]
                heapq.heappush(open_set, (new_f, new_changes, conn['end_stop'], new_time, new_line, new_path))
    
    run_time = time.time() - t0  
    return None, None, run_time



def a_star_min_changes_beam(graph, start_stop, end_stop, start_time, beam_width=100):
    t0 = time.time()
    open_set = []
    heapq.heappush(open_set, (0, 0, start_stop, start_time, None, []))
    best = {}  

    while open_set:
        if len(open_set) > beam_width:
            open_set = heapq.nsmallest(beam_width, open_set)
            heapq.heapify(open_set)

        f, g, current_stop, current_time, current_line, path = heapq.heappop(open_set)
        
        if current_stop == end_stop:
            run_time = time.time() - t0
            return g, path, run_time
        
        if current_stop not in graph:
            continue

        for conn in graph[current_stop]:
            if conn['departure_time'] >= current_time:
                new_line = conn['line']
                new_changes = g

                if current_line is not None and new_line != current_line:
                    wait_delta = conn['departure_time'] - current_time
                    if wait_delta < MIN_CHANGE_TIME:
                        continue 
                    new_changes += CHANGE_COST_PER_CHANGE
                
                new_time = conn['arrival_time']
                state = (conn['end_stop'], new_line)

                if state in best:
                    best_changes, best_time = best[state]
                    if new_changes > best_changes or (new_changes == best_changes and new_time >= best_time):
                        continue

                best[state] = (new_changes, new_time)
                new_f = new_changes 
                new_path = path + [conn]
                heapq.heappush(open_set, (new_f, new_changes, conn['end_stop'], new_time, new_line, new_path))
    
    run_time = time.time() - t0  
    return None, None, run_time