import pandas as pd
from Config.constants import TIME_COST_PER_SEC, CHANGE_COST_PER_CHANGE



def format_schedule_df(path, criterion, start_time=None):
    pd.set_option('display.width', None)       
    pd.set_option('display.max_columns', None)

    if criterion not in ["time", "t", "change", "c"]:
        raise ValueError("wrong criterion")
    
    df = pd.DataFrame(path)
    
    if criterion in ["time", "t"]:
        if start_time is None:
            raise ValueError("For time criterion, start_time must be provided")
            
        costs = []
        for i, row in df.iterrows():
            if i == 0:
                wait = (row['departure_time'] - start_time).total_seconds()
                if wait < 0:
                    wait = 0
                travel = (row['arrival_time'] - row['departure_time']).total_seconds()
                cost = (wait + travel) * TIME_COST_PER_SEC
            else:
                prev_arrival = df.iloc[i-1]['arrival_time']
                wait = (row['departure_time'] - prev_arrival).total_seconds()
                if wait < 0:
                    wait = 0
                travel = (row['arrival_time'] - row['departure_time']).total_seconds()
                cost = (wait + travel) * TIME_COST_PER_SEC
            costs.append(cost)

        df['cost'] = costs
    
    elif criterion in ["change", "c"]:
        costs = [0]
        for i in range(1, len(df)):
            if df.iloc[i]['line'] != df.iloc[i-1]['line']:
                costs.append(CHANGE_COST_PER_CHANGE)
            else:
                costs.append(0)
        df['cost'] = costs

    df['departure_time'] = df['departure_time'].dt.strftime('%H:%M:%S')
    df['arrival_time'] = df['arrival_time'].dt.strftime('%H:%M:%S')
    df = df[['line', 'departure_time', 'start_stop', 'arrival_time', 'end_stop', 'cost']]
    
    return df



def format_tabu_route_df(best_segments, criterion, start_time):
    full_path = []
    for seg in best_segments:
        if seg[2] is not None:
            full_path.extend(seg[2])

    df_route = format_schedule_df(full_path, criterion, start_time)
    return df_route
