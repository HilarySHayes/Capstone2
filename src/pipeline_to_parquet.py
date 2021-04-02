from fitparse import FitFile
import gpxpy
import gzip
import os
import pandas as pd

def semicir_to_degs(semicirc):
    """[Converts from semicircle to degrees]
    Args:
        semicirc ([float]): [lat or long in semicircular units]
    Returns:
        [float]: [lat or long in degree units]
    """
    return semicirc * (180 / 2**31)

def parse_fit(handle):
    """[Parses fit files]
    Args:
        handle: [the handle of the file to be parsed]
    Returns:
        [pandas dataframe]: [dataframe with columns from recorded data
                              converts semicircle lat/long to degrees lat/long]
    """
    try:
        fitfile = FitFile(handle)
        df = pd.DataFrame([{d['name']: d['value'] for d in r.as_dict()['fields']} 
                                   for r in fitfile.get_messages('record')])
        df['position_lat'] = df['position_lat'].map(semicir_to_degs)
        df['position_long'] = df['position_long'].map(semicir_to_degs)  
        return df
    except Exception as e:
        print(f'Issue reading fit file {handle}')

def parse_gpx(handle):
    """[Parses gpx files]
    Args:
        handle: [the handle of the file to be parsed]
    Returns:
        [pandas dataframe]: [dataframe with columns of timestamp, position_lat
                            position_long(in degrees), 'altitude']
    """
    gpx = gpxpy.parse(handle)
    track_coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                track_coords.append([point.time, point.latitude, point.longitude, point.elevation])
    df = pd.DataFrame(track_coords, columns=['timestamp', 'position_lat', 'position_long', 'altitude'])
    return df

def parse_file(filename):
    """[Parses file method depends on file type]
    Args:
        filename: [the name of the file you want to parse]
    Returns:
        [dataframe]: [see output of corresponding parser above]
    """
    if filename.endswith('.fit.gz'):
        handle = gzip.open(filename)
        return parse_fit(handle)
    elif filename.endswith('.gpx'):
        handle = open(filename)
        return parse_gpx(handle)
    elif filename.endswith('.gpx.gz'):
        handle = gzip.open(filename)
        return parse_gpx(handle)
    else:
        print(f'Add parser for {filename} to parse_file function.')

def full_path(directory, filename):
    """[Joins directory and filename to give full path to the file]
    Args:
        directory: [directory name]
        filename: [filename]
    Returns:
        [string]: [full path to the file]
    """
    try:
        return os.path.join(f'../data/{directory}/', filename)
    except Exception as e:
        print(f'Failed to join {filename} in {directory}')
    
def check_file_exists(file):
    """[Checks to see if file exists]
    Args:
        file: [filepath]
    Returns:
        [boolean]: [returns true if filepath exists]
    """
    try:
        return os.path.exists(file)
    except Exception as e:
        print(f'File {file} does not exists')
        
def get_activities(directory):
    """[Gets overview of activity data from the csv file
       creates a pandas dataframe, processes columns, checks
       to see if filename corresponding to activity exists
       returns df sorted by activity data]
    Args:
        directory: [directory]
    Returns:
        [pandas dataframe]: [df of activity overview]
    """
    df = pd.read_csv(f'../data/{directory}/activities.csv')
    df = df[['Activity ID', 'Activity Date', 'Activity Name', 'Activity Type', 
                             'Elapsed Time', 'Distance', 'Filename', 'Moving Time',
                             'Elevation Gain', 'Elevation Loss', 'Average Speed', 'Average Grade']].copy()
    df['Activity Date'] = pd.to_datetime(df['Activity Date'])
    df.columns = [x.lower().replace(" ", "_") for x in df.columns]
    df['filename'] = df['filename'].map(lambda x: full_path(directory, x))
    df['exists'] = df['filename'].map(check_file_exists)
    return df.sort_values('activity_date')

def parquet_activities(person):
    """[Creates a parquet file of the dataframe]
    Args:
        person ([string]): [The name of the folder in ../data 
        where the activity overview file is.]
    """
    act_df = get_activities(person)
    act_df['person'] = person
    print(f'Reading {len(act_df)} activities for {person}. Please be patient as this might take a while!')
    dfs = []
    for i, t in enumerate(act_df.to_dict(orient='records')):
        if i % 40 == 0:
            print(f'{round(100*i/len(act_df),0)} % complete')
        try:
            tmp = parse_file(t['filename'])
            tmp['activity_id'] = t['activity_id']
            tmp['person'] = t['person']
            dfs.append(tmp)
        except Exception as e:
            pass
    print('Creating parquet file')
    df = pd.concat(dfs)
    df['timestamp'] = pd.to_datetime(df['timestamp'].map(lambda x: str(x)[:19]))
    df.to_parquet(f'../data/{person}/df.parquet')

if __name__ == "__main__":

    parquet_activities('Example_Strava')

