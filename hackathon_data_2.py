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
import datetime
from geopy import distance
import fiona
import shapely
import utm



#load data for classification ----------------
vgh_time_df = pd.read_excel("/Users/Natasha/Downloads/Collision Data_Detailed collision data_VGH Injury Data_VGH 2008-2017.xlsx" , index_col = 0).dropna()
vgh_df = pd.read_csv("/Users/Natasha/Desktop/VANquish/collision/VGH_2008-2017.csv", index_col=0)
#pd.read_excel("/Users/Natasha/Desktop/VANquish/collision/VGH_2008-2017.xlsx", index_col=0)
vgh_df['Collision Time Range'] = vgh_time_df['Collision Time Range']

weather_df = pd.read_excel("/Users/Natasha/Desktop/VANquish/Historic_Weather_Lighting2006-2017.xlsx", index_col=0)

traff_sig_df = pd.read_excel("/Users/Natasha/Desktop/VANquish/Traffic_Signals_2.xlsx", index_col=0)

#the geometry of each bikeway in bikeways
shp_file = fiona.open("/Users/Natasha/Desktop/VANquish/bikeways.shx")
bikeways = []
geometry = []
for bikeway in shp_file:
    geometry.append(bikeway['geometry'])
    bikeways.append(shapely.geometry.asShape(bikeway['geometry']))

#functions ----------------
# for a row with month, year, day, return a single date string
def single_date(row):
    if len(str(row['Month'])) < 2:
        return str(row['Year']) + "-" + "0" + str(row['Month']) + "-" + str(row['Day'])
    else:
        return str(row['Year']) + "-" + str(row['Month']) + "-" + str(row['Day'])
    

#for a given time range and date, give the specified weather conditions
def weather_cond(row, weather):
    date = row['Collision Date']
    time_range_str = str(row['Collision Time Range'])
    
    #subset the weather df to particular date
    df = weather_df.loc[weather_df['Collision Date'] == date]
    #get the times for that date
    times = df['Time']
    
    time_range_list = [datetime.datetime.strptime(item, "%H:%M") for item in time_range_str.split("-")]
    start = time_range_list[0].time()
    #end = time_range_list[1].time()
    
    #print(len(times))
    weather_value = ""
    #for all the possible time
    for idx, time in enumerate(times):
        #if the start of the injury is greater, let this be the weather conditions at the time
        if start <= time:
            print(True)
            weather_value = weather_df.iloc[idx]
            weather_value = weather_value[weather]
            break
        
    return weather_value

#for a given accident, get the number of traffic signals in the given radius
def count_traff_sig(row, rad):
    count = 0
    accident_coords = (row['Latitude'], row['Longitude'])
    
    for idx, id in enumerate(traff_sig_df['N/S Street']):
        row_traff = traff_sig_df.iloc[idx]
        traff_sig_coords = (row_traff['Lat'], row_traff['Long'])
        print(traff_sig_coords)
        if distance.distance(accident_coords, traff_sig_coords).km <= radius:
            count += 1
    return count

#for a given accident row, check if the accident's lat lon is on a bike path
def bike_path(row):
    bike_path_bool = False
    for bikeway in bikeways:
        #shape = shapely.geometry.asShape( shapefile_record['geometry'] )
        coords = utm.from_latlon(row['Latitude'], row['Longitude'])
        point = shapely.geometry.Point(coords[0], coords[1]) 
        #print(point)
        if bikeway.distance(point) <= 10000000:
            bike_path_bool = True
            print(True)
            #break
        
    return bike_path_bool


#new variables: weather ---------

#make a singe date column for weather_df
weather_df['Collision Date'] = weather_df.apply(lambda row: single_date (row),axis=1)
#convert to datetime
weather_df['Collision Date'] = weather_df['Collision Date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))

#convert to a datetime date
weather_df['Collision Date'] = weather_df['Collision Date'].apply(datetime.datetime.date)
vgh_df['Collision Date'] = vgh_df['Collision Date'].apply(datetime.datetime.date)


vgh_df['Temp'] = vgh_df.apply(lambda row: weather_cond (row, 'Temp (°C)'),axis=1)
vgh_df['Visibility'] = vgh_df.apply(lambda row: weather_cond (row, 'Visibility (km)'),axis=1)
vgh_df['Weather'] = vgh_df.apply(lambda row: weather_cond (row, 'Weather'),axis=1)

#new variables: traffic ---------

#set radius in km
radius = 0.25

vgh_df['Traffic Signals Count'] = vgh_df.apply(lambda row: count_traff_sig (row, radius),axis=1)

vgh_df.to_csv("/Users/Natasha/Desktop/VANquish/VGH_2008-2017.csv", index=False)
#new variables: bike lane ------

vgh_df['Bike Lane'] = vgh_df.apply(lambda row: bike_path (row),axis=1)


     

