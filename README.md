

<div style="text-align:center"><img src="./images/IMG_1553.jpeg" /></div>

# Strava Peak Clustering

## Background & Motivation

Strava has been a great asset for people wanting to track their exercise endeavors reporting more than 70 million users from more than 190 countries. Living in Colorado where many spend their time hiking, running, skiing, and paragliding off peaks, there are lots of people who use Strava to record their adventures. However there are still features that are lacking. Can we use data science to count the number of time a user has reached the same "peak"? Often there are multiple paths to reach a "peak." For example, how many times has the user summitted the 1st flatiron (Boulder)?  Or how many times have the climbed Mt. Victoria (Frisco)?

## Data

I collected private [Strava](https://www.strava.com/) data from Colorado athletes.  For each activity, an athlete has an overview summary including information such as activity type, date, elapsed time, distance, the associated filename, elevation gain, elevation low/high, and much more. Combining atheletes there were more than recorded activities. 

'| Activity Date             |   Activity ID | Activity Name   | Activity Type   |   Elapsed Time |   Distance | Commute   | Filename                     |   Moving Time |   Max Speed |   Elevation Gain |   Elevation Low |   Elevation High |   Max Grade |   Average Grade |   Average Temperature |\n|:--------------------------|--------------:|:----------------|:----------------|---------------:|-----------:|:----------|:-----------------------------|--------------:|------------:|-----------------:|----------------:|-----------------:|------------:|----------------:|----------------------:|\n| Jul 19, 2018, 11:54:08 AM |    1714403192 | Morning Hike    | Hike            |          43352 |      44.33 | False     | activities/1839577269.fit.gz |         38527 |         3.4 |             2287 |          2934.6 |           3748.2 |        43.3 |       0.0248099 |                    24 |'

For each activity, 