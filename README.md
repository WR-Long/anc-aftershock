# Anchorage Aftershock Plot
This project is a single Python script for generating a plot of aftershocks following the 30-Nov-2018 M 7.0 earthquake near Anchorage, Alaska.  The plot is used in a webpage found at the following address: https://www.optimalicity.com/p/anc-aftershock.html

## Data Wrangling
Data is downloaded as a GeoJSON from USGS for all M 1.0+ earthquakes in the past 7 days.  The pandas library is used to retrieve the JSON file and parse to a data frame.  The GeoPy library is used to calculate distance based on latitude and longitude for filtering to only earthquakes within 100 miles of Anchorage.  The output plot is saved as a *.png file with Matplotlib.

## Implementation
The script runs on a AWS EC2 instance for the 6 days following the earthquake.  The script puts the generated plot image in an AWS S3 bucket.  The image URL is used in the Blogger page.  A cron job executes the script every 5 minutes to retrieve the JSON that is updated every 5 minutes by USGS.