

<div style="text-align:center"><img src="./images/IMG_1553.jpeg" /></div>

# Strava Peak Clustering

## Background & Motivation

Strava is a great asset for people wanting to track their exercise endeavors reporting more than 70 million users from more than 190 countries. Living in Colorado, where many spend their time hiking, running, skiing, and paragliding off peaks, there are lots of people who use Strava to record their adventures. While Strava provides many paid and unpaid features, there are still features that are lacking that we can use data science to answer. For example, how many times has a user reached the same "peak"? Often there are multiple paths to reach a "peak". For example, how many times has the user summitted the 1st Flatiron, a 5th class climb in Boulder, CO?  Or how many times have they climbed Mt. Victoria, towering over Frisco, CO?

## Data

I collected private [Strava](https://www.strava.com/) data from a few Colorado athletes.  For each activity, an athlete has an overview summary including information such as activity date, type, elapsed time, distance, the associated filename, elevation gain, elevation low/high, and much more. Combining athletes there were more than 5000 recorded activities. 

    | Activity Date            |   Activity ID | Activity Name   | Activity Type   |   Elapsed Time |   Distance | Commute   | Filename                     |   Moving Time |   Max Speed |   Elevation Gain |   Elevation Low |   Elevation High |   Max Grade |   Average Grade |   Average Temperature |
    |--------------------------|---------------|-----------------|-----------------|----------------|------------|-----------|------------------------------|---------------|-------------|------------------|-----------------|------------------|-------------|-----------------|-----------------------|
    | Jul 19, 2018, 11:54:08 AM|    1714403192 | Morning Hike    | Hike            |          43352 |      44.33 | False     | activities/1839577269.fit.gz |         38527 |         3.4 |             2287 |          2934.6 |           3748.2 |        43.3 |       0.0248099 |                    24 |

For each activity, there is a file containing more detailed information about the activity often collected at second intervals throughout the activity. There were multiple different formats including: .gpx, .tcx, .fit file types to handle.  Even for a single user the method used to record each activity varied due to changing watches, using a cellphone etc. As a result the recorded data varied in what it contained.  It was not uncommon within an activity to be missing latitude, longitude, or altitude for multiple second intervals.  Sme devices used were not capable of collecting elevation data in which case for those activities all elevation data is missing. 


    |    | timestamp           |   position_lat |   position_long |   distance |   altitude |   speed |   cadence |   temperature |
    |----|---------------------|----------------|-----------------|------------|------------|---------|-----------|---------------|
    |  0 | 2015-12-12 18:41:42 |        40.0201 |        -105.298 |       0    |     1698.8 |   0     |         0 |            23 |
    |  1 | 2015-12-12 18:41:45 |        40.0202 |        -105.298 |       0    |     1698.8 |   4.535 |        59 |            23 |
    |  2 | 2015-12-12 18:41:56 |        40.02   |        -105.298 |      20.55 |     1698.8 |   3.602 |        93 |            23 |



## Clustering Peaks

Not all activities involve a peak. In order to filter activities that I belive to be a peak experience, I looked for activities that had a `gain_threshold` that is approximately 400 meters.  Activities that met this criteria are considered in our peak clustering.

This list gives a starting point for clustering peaks.  For each activity, I picked out the latitude and longitude values that corresponded to the highest location.  This new data set, of one point per activity, that represents the peak, was used to cluster the activities into similar peaks using a distance threshold.  I used `DBSCAN`, which is part of  `scikit-learn` to do the clustering.

The `DBSCAN` algorithm has a distance threshold that has a very intuitive meaning and for this application, is the distance between peaks that should be classified together.  To visually verify that I have the correct value for this critical parameter, I mapped the peaks and color coded different cluster to visually see how `DBSCAN` performed and then refined the value based on what I belived to be the best clustering.  Future work will investigate if this performs well across a variety of different athletes and terrain choices.

As mentioned above, not all activites had altitude information.  Once the peaks had been identified, I was able to scan through previously uncategorized activities to identify tracks that had come within the epsilon distance used by `DBSCAN` to further increase the accuracy of my peak counts.  Unfortunately, it is still possible that some activites that involved a peak experience for which there is no altitude data, and therefore, a blind spot in this analysis.

## Results

I applied the algorithm described above to two different data sets.  The first is a friend who love climbing the first flatiron in Boulder, CO, but would love to know how many times he's climbed that route and some basic statistics that surround this group of data.  The second data set is from an athlete that frequently climbs Mount Victoria and runs, skis, or even paraglides off the summit.  How often has this person summited?





## Future Directions

This is a first step toward understanding the statistics that surround summitting and repeating peaks.  As a recap of the work done, I have filtered activities by their highest point keeping those above a specific threshold, clustered the peaks for which I had altitude data, and associated activites for which I didn't have altitude data with the cluster peaks.  This gives an estimate of peaks were climbed and how often.

There are, of course, different ways to enjoy these peaks and being able to detect changes in mode would be an interesting next step.  For example, running up and down might not look too different when accounting for altitude gain or loss, but skiiing up and down might have a more dramatic and learnable feature.  What about a bike ride to the trail head, hike up the peak, and then paragliding back home?  Can I identify these differnt segments.  Similarly, although not a multisport activity, sometimes atheletes drive away when they are done.  Can I detect this transition to a new mode of transportation?  Could this be auto-corrected in the future or could your watch ask you if you still want to be recording?
