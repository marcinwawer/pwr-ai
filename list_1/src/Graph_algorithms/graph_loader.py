from datetime import datetime, timedelta
import csv
from src.Config.constants import FILE_NAME



def parse_extended_time(time_str):
    h, m, s = map(int, time_str.split(':'))
    extra_days, hour = divmod(h, 24)
    base_date = datetime(1900, 1, 1) 
    return base_date + timedelta(days=extra_days, hours=hour, minutes=m, seconds=s)



def load_weighted_graph(criterion):
    if criterion not in ["time", "t", "change", "c"]:
        raise ValueError("wrong criterion")

    graph = {}
    with open(FILE_NAME, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                row['departure_time'] = parse_extended_time(row['departure_time'])
                row['arrival_time'] = parse_extended_time(row['arrival_time'])
                row['start_stop_lat'] = float(row['start_stop_lat'])
                row['start_stop_lon'] = float(row['start_stop_lon'])
                row['end_stop_lat'] = float(row['end_stop_lat'])
                row['end_stop_lon'] = float(row['end_stop_lon'])
            except Exception as e:
                continue  

            if criterion in ['time', 't']:
                row['weight'] = (row['arrival_time'] - row['departure_time']).total_seconds
            elif criterion in ['change', 'c']:
                row['weight'] = 0

            start = row['start_stop']
            if start not in graph:
                graph[start] = []
            graph[start].append(row)
    
    return graph