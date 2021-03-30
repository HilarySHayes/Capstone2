
from fitparse import FitFile
import gzip
import gpxpy
import numpy as np
import os
import pandas as pd

def semicir_to_degs(semicirc):
    return semicirc * (180 / 2**31)

def parse_fitgz(filename):
    try:
        fitfile = FitFile(gzip.open(filename))
        df = pd.DataFrame([{d['name']: d['value'] for d in r.as_dict()['fields']} 
                                   for r in fitfile.get_messages('record')])
        df['position_lat'] = df['position_lat'].map(semicir_to_degs)
        df['position_long'] = df['position_long'].map(semicir_to_degs)
        return df
    except Exception as e:
        print(f'Issue reading fit file {filename}.')

def parse_gpx(filename):
    gpx = gpxpy.parse(filename)
    track_coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                track_coords.append([point.time, point.latitude, point.longitude, point.elevation])
    return pd.DataFrame(track_coords, columns=['position_lat', 'position_long', 'altitude'])

def parse_file(filename):
    if filename.endswith('.fit.gz'):
        return parse_fitgz(filename)
    elif filename.endswith('.gpx'):
        return parse_gpx(filename)
    elif filename.endswith('.gpx.gz'):
        return parse_gpx(gzip.open(filename))
    else:
        print(f'Add parser for {filename} to parse_file function.')

def full_path(directory, filename):
    try:
        return os.path.join(f'../data/{directory}/', filename)
    except Exception as e:
        print(f'Full_path error directory: {directory}, {filename}')

def check_file_exists(file):
    try:
        return os.path.exists(file)
    except Exception as e:
        print(f'File {file} does not exist')
        
def get_activities(directory):
    df = pd.read_csv(f'../data/{directory}/activities.csv')
    df = df[['Activity ID', 'Activity Date', 'Activity Name', 'Activity Type', 
                             'Elapsed Time', 'Distance', 'Filename', 'Moving Time',
                             'Elevation Gain', 'Elevation Loss', 'Average Speed', 'Average Grade']]
    df['Activity Date'] = pd.to_datetime(df['Activity Date'])
    df.columns = [ x.lower().replace(" ", "_") for x in df.columns]
    df['filename'] = df['filename'].map(lambda x: full_path(directory, x))
    df['exists'] = df['filename'].map(check_file_exists)
    return df.sort_values('activity_date')

def combine_everyone_into_df(folder_list):
    dfs = []
    for folder in folder_list:
        df = get_activities(folder)
        df['person'] = folder
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def pickle_activities(folder_list):
    everyone_df = combine_everyone_into_df(folder_list)  
    for person in folder_list:
        dfs = []
        current = everyone_df[everyone_df.person == person]
        for i, d in enumerate(current.to_dict(orient='records')):
            if i%20==0:
                print(i, len(dfs))
            try:
                df = parse_file(d['filename'])
                df['activity_id'] = d['activity_id']
                df['person'] = d['person']
                dfs.append(df)
            except Exception as e:
                pass
        person_df = pd.concat(dfs)
        person_df['timestamp'] = pd.to_datetime(person_df['timestamp'].map(lambda x: str(x)[:19]))
        person_df.to_pickle(f'../data/{person}/df.pkl')
    

if __name__ == '__main__':
    # everyone = combine_everyone_into_df(['MB_Strava', 'BL_Strava', 'KM_Strava', 'LB_Strava'])
    # print(everyone.tail(10))
    # print(everyone.shape)
    pickle_activities(['BK_Strava', 'MB_Strava', 'BL_Strava', 'KM_Strava', 'LB_Strava'])