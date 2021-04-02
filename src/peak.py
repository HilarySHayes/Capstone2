import folium
import itertools
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

def max_altitude(act):
    """[Find the highest point in an activity]
    Args:
        act: [pandas dataframe for activity
                with altitude column]
    Returns:
        highest_pt: [panda dataframe with single row corresponding 
        to when the highest point was acheived. Has new column gain 
        marking the difference between the highest pt and lowest point]
    """
    index = act['altitude'].idxmax()
    diff = act['altitude'].max() - act['altitude'].min()
    highest_pt = act.loc[index]
    highest_pt['gain'] = diff
    return highest_pt

def peak_detector(df, gain_threshold):
    """[Filters activities df retaining activities where the gain 
        in altitude is more than the specified threshold]
    Args:
        df ([pandas dataframe]): [activities df]
        gain_threshold ([float]): [filter df keeping activities 
        where altitude gain more than this threshold]
    Returns:
        [pandas dataframe]: [df containing activities where the 
        altitude gain is great than the specified gain threshold]
    """
    #df.rename(columns={'alt': 'altitude', 'lat': 'position_lat', 'lon': 'position_long'}, inplace=True) 
    with_alt = df.dropna(subset=['altitude'])
    peaks = with_alt.groupby('activity_id').apply(max_altitude)
    peaks = peaks[peaks['gain'] > gain_threshold]
    return peaks

def plot_one_cluster(m, df, activities_ids, steps, color):
    """[Adds plots lat/long position for each activity 
        in the list of activities_ids to a folium map]
    Args:
        m ([folium map object]): [a folium map object where the plot]
        df ([pandas dataframe]): [df with colums position_lat, position_long, and activity_id]
        activities_ids ([list]): [list of activity_id for which you wish to plot the path taken]
        steps ([int]): [plots every steps-th lat/long]
    """
    for activity_id in activities_ids:
        locations = df.query(f'activity_id=={activity_id}')[['position_lat', 'position_long']].iloc[::steps]
        locations.dropna(inplace=True)
        points = locations.values.tolist()
        folium.PolyLine(points, color=color, weight=2.5, opacity=0.5).add_to(m)

def plot_multiple_clusters(df, peaks, colormap, cluster_series, steps):   
    """[Plots multiple clusters of peaks on a folium map]
    Args:
        df ([pandas dataframe]): [df with colums position_lat, position_long, and activity_id]
        peaks ([pandas dataframe]): [df with peaks lat/long]
        colormap ([array]): [array of colors to use]
        cluster_series ([type]): [description]
        steps ([int]): [plots every steps-th lat/long]
    Returns:
        [folium map object]: [folium map object]
    """
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
    """[Clusters activities]
    Args:
        peaks ([pandas dataframe]): [df with peaks lat/long]
        epsilon ([float]): [parameter for DBSCAN local radius for expanding clusters]
        min_samples (int, optional): [minimun number of samples for cluster]. Defaults to 2.
    Returns:
        [pandas series]: [index is cluster number, values are number of activities belonging to that cluster]
    """
    clustering = DBSCAN(eps=epsilon, metric='haversine', min_samples=min_samples).fit(peaks[['position_lat', 'position_long']])
    peaks['cluster'] = clustering.labels_ 
    frequency = peaks['cluster'].value_counts().sort_values(ascending=False)
    cluster_series = frequency[frequency.index != -1]
    return cluster_series

def save_cluster_plot(person, epsilon, colormap, filename, gain_threshold=400, steps=10):
    """[Saves the clusterplot]
    Args:
        person ([string]): [The name of the folder in ../data 
        where activity files are.]
        epsilon ([float]): [parameter for DBSCAN local radius for expanding clusters]
        colormap ([array]): [array of colors to use]
        filename ([string]): [name of the output file]
        gain_threshold (float, optional): [filter df keeping activities 
        where altitude gain more than this threshold]. Defaults to 400.
        steps (int, optional): [plots every steps-th lat/long]. Defaults to 10.
    Returns:
        [pandas series]: [index is cluster number, values are number of activities belonging to that cluster]
    """
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
    
    epsilon = 0.001 

    person = 'Example_Strava'
    b = save_cluster_plot(person, epsilon, colormap, 'Example')
    print(b)
