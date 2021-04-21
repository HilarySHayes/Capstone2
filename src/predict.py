from branca.element import Template, MacroElement
import folium
from functools import partial
from geopy import distance
import numpy as np
import pandas as pd
import pickle
import legend_helper

def resample_activity(df, interval="30s"):
    """[resamples from the dataframe]
    Args:
        df ([pandas dataframe]): [df you will sample from]
        interval ([string]): [interval at which you want to resample]
    Returns:
        [pandas dataframe]: [dataframe resampled at the specified 
        interval averaged over the interval]
    """
    return df.resample(interval).mean().drop('activity_id', axis='columns')

def compute_speed_distance(df):
    """[Takes df with position_lat, position_long, altitude, and time and 
        calculates change in altitude, time, distance, speed]
    Args:
        df ([pandas dataframe]): [df with position_lat, position_long, altitude, and time]
    Returns:
        [pandas dataframe]: [df with distance, change in time, change in altitude, speed]
    """
    df = df.reset_index()
    df['lon_previous'] = df['position_long'].shift(1)
    df['lat_previous'] = df['position_lat'].shift(1)
    df['alt_previous'] = df['altitude'].shift(1)
    df['time_previous'] = df['time'].shift(1)
    df = df.fillna(method='bfill')
    df['distance_dis_2d'] = df.apply(lambda x: distance.distance((x['lat_previous'], x['lon_previous']), (x['position_lat'], x['position_long'])).m, axis = 1)
    df['delta_alt'] = df.apply(lambda x: x['altitude']- x['alt_previous'], axis=1)
    df['distance'] = df.apply(lambda x: np.sqrt(x['distance_dis_2d']**2 + (x['delta_alt'])**2), axis=1)
    df['time_delta'] = df.apply(lambda x: (x['time'] - x['time_previous']).total_seconds(), axis=1)
    df['speed'] = df['distance'].divide(df['time_delta'])
    return df

def window_features(df, speed_thres=0, window=2*5):
    """[From dataframe with speed, distance, time, and change in altitude 
        calculates mean, max, and std of these over a rolling window]
    Args:
        df ([pandas dataframe]): [dataframe with speed, distance, time, and change in altitude]
        speed_thres (int, optional): [Threshold for speed. Only keeps rows when
                                       speed is >= this threshold]. Defaults to 0.
        window (int, optional): [size of the moving window over which you
                                 are calculating. Length of time is affected by
                                 resampling]. Defaults to 2*5, when resampling is 30s
                                 this is a window of 5 min.
    Returns:
        [pandas df]: [a windowed dataframe]
    """
    df = df.query(f"speed >= {speed_thres}")
    month = df['time'].dt.month
    dist = df['distance'].rolling(window).mean()
    dist_max = df['distance'].rolling(window).max()
    dist_std = df['distance'].rolling(window).std()
    speed = df['speed'].rolling(window).mean()
    speed_max = df['speed'].rolling(window).max()
    speed_std = df['speed'].rolling(window).std()
    delta_alt = df['delta_alt'].rolling(window).mean()
    delta_alt_max = df['delta_alt'].rolling(window).max()
    delta_alt_std = df['delta_alt'].rolling(window).std()
    final_df = pd.concat([dist, dist_max, dist_std, 
                    speed, speed_max, speed_std,
                    delta_alt, delta_alt_max, delta_alt_std, month], axis=1)
    final_df.columns = ['dist', 'dist_max', 'dist_std', 
                  'speed', 'speed_max', 'speed_std',
                  'delta_alt', 'delta_alt_max', 'delta_alt_std', 'month']
    return final_df

def evaluate_mode(filename, clf, speed_thres=0, window=2*5, interval="30s"):
    """[Imports activity, converts to dataframe, predicts activity type
        for each segment of activity]
    Args:
        filename ([string]): [filepath]
        clf ([model]): [fit classification model]
        speed_thres (int, optional): [Threshold for speed. Only keeps rows when
                                       speed is >= this threshold]. Defaults to 0.
        window (int, optional): [size of the moving window over which you
                                 are calculating. Length of time is affected by
                                 resampling]. Defaults to 2*5, when resampling is 30s
                                 this is a window of 5 min.
        interval ([string]): [interval at which you want to resample] Defaults to 30s
    Returns:
        [pandas df]: [dataframe for activity including predictions of activity
                      type for each segment]
    """
    sample_df = pd.read_parquet(filename)
    sample_df['time'] = pd.to_datetime(sample_df['time'], utc=True)
    sample_df['time'] = sample_df['time'].dt.tz_localize(tz=None)
    sample_df.set_index('time', inplace=True)
    resample_activity_instance = partial(resample_activity, interval=interval)
    sample_df = sample_df.groupby(['activity_id']).apply(resample_activity_instance).reset_index().set_index('time')
    sample_df = sample_df.fillna(method='ffill')
    sample_df = sample_df.fillna(method='bfill')
    sample_df = compute_speed_distance(sample_df)
    sample_data = window_features(sample_df, speed_thres, window)
    sample_data = sample_data.dropna()
    X = sample_data.values
    sample_df.loc[ sample_data.index , 'predicted_mode'] = clf.predict(X)
    return sample_df[['time', 'position_lat', 'position_long', 'predicted_mode']].dropna(axis=0)

def visualize_prediction(df, color_dict, save_to):
    """[Creates folium map of activity path colored by predicted activity type]
    Args:
        df ([pandas df]): [dataframe of activity data including position_lat, position_long
                            and predicted_mode, the predicted activity type]
        color_dict ([dictionary]): [keys are activity types, values are colors]
        save_to ([string]): [filepath where folium map is saved]
    Returns:
        [folium.Map object]: [folium map of activity path colored by predicted activity type]
    """
    df['break'] = df['predicted_mode']==df['predicted_mode'].shift(1)
    df['segment'] = None
    segment = 0
    rows = []
    for row in df.to_dict(orient='records'):
        if not row['break']:
            row['segment'] = segment
            segment += 1
        rows.append(row)            
    df = pd.DataFrame(rows).fillna(method='ffill')

    central_lat = df.position_lat.mean()
    central_long = df.position_long.mean()
    m = folium.Map(location=[central_lat,central_long],tiles="Stamen Terrain",zoom_start=14.5)
    for segment in df.segment.unique():
        locations = df.query(f"segment=={segment}")[['position_lat', 'position_long']]
        act_type = df.query(f"segment=={segment}")[['predicted_mode']].values[0][0]
        folium.PolyLine(locations.values.tolist(), color=color_dict[act_type], weight=2.5, opacity=0.9).add_to(m)
    macro = MacroElement()
    macro._template = Template(legend_helper.legend_string)
    m.add_child(macro)
    m.save(save_to)
    return m

if __name__ == '__main__':
    with open('../data/model.pkl', 'rb') as f:
        clf = pickle.load(f)
    activity_id = 4408957556
    filename = f'../data/samples/sample{activity_id}.parquet'
    final_df = evaluate_mode(filename, clf)
    activity_types = final_df.predicted_mode.unique()
    print(activity_types)
    color_dict = {'fly_down':'#e41a1c', 'run_down':'#ffff33', 
                    'run_up':'#377eb8', 'ski_up': '#984ea3', 
                    'ski_down': '#ff7f00'}
    save_to = f'../images/predictions_for_{activity_id}.html'
    visualize_prediction(final_df, color_dict, save_to)
