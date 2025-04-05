from datetime import datetime
import csv
from Config.constants import FILE_NAME

def load_weighted_graph(criterion):
    if criterion not in ["time", "t", "change", "c"]:
        raise ValueError("wrong criterion")

    graph = {}
    with open(FILE_NAME, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                row['departure_time'] = datetime.strptime(row['departure_time'], "%H:%M:%S")
                row['arrival_time'] = datetime.strptime(row['arrival_time'], "%H:%M:%S")
                row['start_stop_lat'] = float(row['start_stop_lat'])
                row['start_stop_lon'] = float(row['start_stop_lon'])
                row['end_stop_lat'] = float(row['end_stop_lat'])
                row['end_stop_lon'] = float(row['end_stop_lon'])
            except Exception as e:
                continue  

            if criterion == 'time' or criterion == "t":
                row['weight'] = (row['arrival_time'] - row['departure_time']).seconds
            elif criterion == 'change' or criterion == "c":
                row['weight'] = 0

            start = row['start_stop']

            if start not in graph:
                graph[start] = []

            graph[start].append(row)
    
    return graph