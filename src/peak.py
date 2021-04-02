import folium
import itertools
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

def max_altitude(act):
    index = act['altitude'].idxmax()
    diff = act['altitude'].max() - act['altitude'].min()
    highest_pt = act.loc[index]
    highest_pt['gain'] = diff
    return highest_pt

def peak_detector(df, gain_threshold):
    df.rename(columns={'alt': 'altitude', 'lat': 'position_lat', 'lon': 'position_long'}, inplace=True) 
    with_alt = df.dropna(subset=['altitude'])
    peaks = with_alt.groupby('activity_id').apply(max_altitude)
    peaks = peaks[peaks['gain'] > gain_threshold]
    return peaks

def plot_one_cluster(m, df, activities_ids, steps, color):
    for activity_id in activities_ids:
        locations = df.query(f'activity_id=={activity_id}')[['position_lat', 'position_long']].iloc[::steps]
        locations.dropna(inplace=True)
        points = locations.values.tolist()
        folium.PolyLine(points, color=color, weight=2.5, opacity=0.5).add_to(m)

def plot_multiple_clusters(df, peaks, colormap, cluster_series, steps):   
    central_lat, central_long = peaks.query(f'cluster=={cluster_series.idxmax()}')[['position_lat', 'position_long']].mean()
    n = len(list(cluster_series.index))
    m = folium.Map(location=[central_lat, central_long],tiles='Stamen Terrain', zoom_start=12)
    peak_positions = peaks.groupby('cluster')[['position_lat', 'position_long']].mean()
    for i, val in enumerate(list(cluster_series.index)):
        color = next(colormap)
        activities_ids = list(peaks.query(f'cluster=={val}').index)
        plot_one_cluster(m, df, activities_ids, steps, color)
        peak = peak_positions.loc[val]
        folium.CircleMarker(location=[peak['position_lat'], peak['position_long']],radius=10, color=color).add_to(m)
    return m

def peak_clustering(peaks, epsilon, min_samples=2):
    clustering = DBSCAN(eps=epsilon, metric='haversine', min_samples=min_samples).fit(peaks[['position_lat', 'position_long']])
    peaks['cluster'] = clustering.labels_ 
    frequency = peaks['cluster'].value_counts().sort_values(ascending=False)
    cluster_series = frequency[frequency.index != -1]
    return cluster_series

def save_cluster_plot(person, epsilon, colormap, filename, gain_threshold=400, steps=10):
    person_df = pd.read_parquet(f'../data/{person}/df.parquet')
    peaks = peak_detector(person_df, gain_threshold)
    peaks = peaks.dropna(subset=['position_lat', 'position_long'])
    cluster_series = peak_clustering(peaks, epsilon)
    m = plot_multiple_clusters(person_df, peaks, colormap, cluster_series, steps)
    m.save(f'../html/{filename}.html')
    return cluster_series

if __name__ == '__main__':
    colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c',
            '#fb9a99','#e31a1c','#fdbf6f','#ff7f00',
            '#cab2d6','#6a3d9a','#ffff99','#b15928']
    colormap = itertools.cycle(colors)
    
    person = 'KM_Strava'
    epsilon = 0.0009 #0.0005
    s = save_cluster_plot(person, epsilon, colormap, 'Summit')
    print(s)

    person = 'BL_Strava'
    # b = save_cluster_plot(person, epsilon, colormap, 'Boulder')
    # print(b)
