#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 22:19:04 2018

@author: Natasha
"""

#import json
#from shapely.geometry import shape, Point
#import utm

import pandas as pd
from math import cos, asin, sqrt


#load data for classification ----------------
senior_df = pd.read_excel("/Users/Natasha/Desktop/VANquish Data/GeospatialData_Community amenities_Seniors Homes_Seniors Homes.xls")
vgh_df = pd.read_csv("/Users/Natasha/Desktop/VANquish/VGH_2008.2017.final.csv", index_col=0)

#-----------

def distance_lat_lon(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))


def closest(data, point_row, field):
    p_lon = point_row['LONG']
    p_lat = point_row['LAT']
    min_distance = 100000
    for index, row in vgh_df.iterrows():
        dist = distance_lat_lon(p_lat,p_lon, row['Latitude'],row['Longitude'])
        if dist < min_distance:
            #update
            min_distance = dist
            idx = 0
    closest_row = vgh_df.iloc[idx]
    return closest_row['severe.prob']
    


#-----------
    
senior_df['minor.prob'] = senior_df.apply(lambda row: closest(vgh_df, row, 'minor.prob'),axis=1)
senior_df['severe.prob'] = senior_df.apply(lambda row: closest(vgh_df, row, 'severe.prob'),axis=1)
