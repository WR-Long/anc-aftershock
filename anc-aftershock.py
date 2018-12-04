# -*- coding: utf-8 -*-
"""
Download earthquakes, plot, publish.
"""

import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from geopy import distance
import matplotlib.pyplot as plt
import datetime
import boto3

def colors(intensity):
    c = pd.DataFrame(intensity)
    c = c.round()
    c = c.fillna('#FFFFFF')
    c[c == 0] = '#FFFFFF'
    c[c == 1] = '#FFFFFF'
    c[c == 2] = '#BFCCFF'
    c[c == 3] = '#A0E6FF'
    c[c == 4] = '#80FFFF'
    c[c == 5] = '#7AFF93'
    c[c == 6] = '#7AFF00'
    c[c == 7] = '#FFC800'
    c[c == 8] = '#FF9100'
    c[c == 9] = '#FF0000'
    c[c == 10] = '#D20000'
    c = pd.Series(c.iloc[:,0])
    return c

#Retrieve GeoJSON from USGS (M 1.0+, Past 7 Days)
url='https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson'
df = pd.read_json(url, typ='table')
#Keep only features
df = json_normalize(df.features)
anc = (61.216667, -149.9) #Anchorage Latitude, Longitude
#Calculate distance to each quake
latlon = df['geometry.coordinates'].apply(lambda x: (x[1],x[0]))
dist = latlon.apply(lambda x: distance.distance(anc, x).miles)
df.insert(0, 'dist', dist)
df = df.where(df.dist <= 100) #Plot only quakes within 100 miles
df = df.dropna(how='all')
#Convert to local time
df['properties.time'] = df['properties.time'] + df['properties.tz']*60*1000
df['properties.time'] = pd.to_datetime(df['properties.time'], unit='ms')
#Count total
tot = str(df.shape[0])
#Plot
fig = plt.figure()
fig.set_size_inches(16*.75, 9*.75)
ax = fig.add_subplot(111)
c = colors(df['properties.mmi'])
c = c.ravel()
ax.scatter(df['properties.time'].values,
           df['properties.mag'],
           df['properties.mag']**3,
           c,
           linewidths=0.5,
           edgecolors='k')
tot = tot + ' total earthquakes in the last 7 days'
ax.annotate(tot,
            xy=(0.8, 0.9), xycoords='axes fraction',
            xytext=(0.9, 0.9), textcoords='axes fraction',
            horizontalalignment='right', verticalalignment='top')
ax.set_title('Earthquakes within 100 Miles of Anchorage, Alaska', fontsize=20)
ax.set_xlabel('Time (AKST)')
ax.set_xlim(np.datetime64('2018-11-30T07:00'),
            np.datetime64('2018-12-06T07:00'))
ax.set_ylabel('Magnitude')
ax.set_yscale('log')
ax.set_ylim(1,8)
plt.tick_params(axis='y', which='minor')
ax.get_yaxis().set_minor_formatter(plt.FuncFormatter(
    lambda x, loc: "{:,}".format(int(x))))
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(
    lambda x, loc: "{:,}".format(int(x))))
ax.grid(True, which='both')
ax.text(-0.05, -0.15, ('Data: earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php\n' +
                   'Plot: optimalicity.com/p/anc-aftershock.html'),
        fontsize=10, ha='left', va='bottom', color='.5', transform=ax.transAxes)
plt.savefig('anc_aftershock.png')
now = datetime.datetime.now().strftime('%Y-%b-%dT%H%M%S')
now = 'anc_aftershock_' + now + '.png'
plt.savefig(now)
#Upload to S3
s3 = boto3.resource('s3')
data = open('anc_aftershock.png', 'rb')
s3.Bucket('anc-aftershock').put_object(Key='anc_aftershock.png', Body=data,
          ACL='public-read', ContentType='image/png')
data = open(now, 'rb')
s3.Bucket('anc-aftershock').put_object(Key=now, Body=data,
          ACL='public-read', ContentType='image/png')