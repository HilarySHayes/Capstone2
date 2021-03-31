

<div style="text-align:center"><img src="./images/IMG_1553.jpeg" /></div>

# Strava Peak Clustering

## Background & Motivation

Strava has been a great asset for people wanting to track their exercise endeavors reporting more than 70 million users from more than 190 countries. Living in Colorado where many spend their time hiking, running, skiing, and paragliding off peaks, there are lots of people who use Strava to record their adventures. However there are still features that are lacking. Can we use data science to count the number of time a user has reached the same "peak"? Often there are multiple paths to reach a "peak." For example, how many times has the user summitted the 1st flatiron (Boulder)?  Or how many times have the climbed Mt. Victoria (Frisco)?

## Data

I collected private [Strava](https://www.strava.com/) data from a few Colorado athletes.  For each activity, an athlete has an overview summary including information such as activity date, type, elapsed time, distance, the associated filename, elevation gain, elevation low/high, and much more. Combining athletes there were more than 5000 recorded activities. 

    | Activity Date             |   Activity ID | Activity Name   | Activity Type   |   Elapsed Time |   Distance | Commute   | Filename                     |   Moving Time |   Max Speed |   Elevation Gain |   Elevation Low |   Elevation High |   Max Grade |   Average Grade |   Average Temperature |
    |:--------------------------:|:--------------:|:----------------:|:----------------:|:---------------:|:-----------:|:----------:|:-----------------------------:|:--------------:|:------------:|:-----------------:|:----------------:|:-----------------:|:------------:|:----------------:|:----------------------:|
    | Jul 19, 2018, 11:54:08 AM |    1714403192 | Morning Hike    | Hike            |          43352 |      44.33 | False     | activities/1839577269.fit.gz |         38527 |         3.4 |             2287 |          2934.6 |           3748.2 |        43.3 |       0.0248099 |                    24 |

For each activity, there is a file containing more detailed information about the activity often collected at second intervals throughout the activity. There were multiple different formats including: .gpx, .tcx, .fit file types to handle.  Even for a single user the method used to record each activity varied from changing watches to using a cellphone etc. As a result the recorded data varied in what it contained.  It was not uncommon within an activity to be missing latitude, longitude, or altitude for multiple second intervals.  As some devices used were not capable of collecting elevation data in which case for those activities all elevation data is missing. 


    |    | timestamp           |   position_lat |   position_long |   distance |   altitude |   speed |   cadence |   temperature |
    |:---:|:--------------------:|:---------------:|:----------------:|:-----------:|:-----------:|:--------:|:----------:|:--------------:|
    |  0 | 2015-12-12 18:41:42 |        40.0201 |        -105.298 |       0    |     1698.8 |   0     |         0 |            23 |
    |  1 | 2015-12-12 18:41:45 |        40.0202 |        -105.298 |       0    |     1698.8 |   4.535 |        59 |            23 |
    |  2 | 2015-12-12 18:41:56 |        40.02   |        -105.298 |      20.55 |     1698.8 |   3.602 |        93 |            23 |
