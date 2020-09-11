# COVIDTracking-to-AGOL

In early 2020, the novel Coronavirus (SARS-CoV-2), also known as COVID-19 swept across the globe. The COVID Tracking Project ([covidtracking.com](https://covidtracking.com)) was started by journalists at *The Atlantic* to help their investigation into lagging COVID-19 testing rates. Their dataset has evolved to become one of the most complete datasets available by state in the United States for testing, hospitalizations, and deaths for COVID-19. Their data consumes the data reported by each state's department of public health official and provides the data in a single source. Without their tireless efforts, this project would not be possible.

In short, what this script does is scrape their API and adds their data to a table on ArcGIS Online. This allows the data to be consumed by a geospatial application. The script can be scheduled to run on a regular basis and help provide daily updates for COVID-19 across the country.

# Setup
To run this script, you must store your ArcGIS Online (AGOL) credentials locally. Please consult [this documentation](https://developers.arcgis.com/python/guide/working-with-different-authentication-schemes/#Storing-your-credentials-locally) if you're unfamiliar with the process.

## Storing credentials locally
When I set up my credentials, I used the following code in my python terminal:
```
from arcgis import GIS
prof = GIS(url='https://arcgis.com',username='your.username',password='P@$sw0rd123!',profile='AGOL'
```
In this script, you will need to switch the ```gis = GIS(profile='AGOL')``` variable to whatever you named your stored credential profile.

A good test to make sure it all worked is to run 
```gis = GIS(profile='AGOL')
gis.users.me.username
```
If it returns with your AGOL username, you're all set!

## Setting up the table ID
This script relies on being able to write data to a table on AGOL. The AGOL feature ID is at the end of the AGOL url ```../item.html?id=<some_string>```.
[This blog post](https://community.esri.com/community/gis/web-gis/arcgisonline/blog/2019/06/06/where-can-i-find-the-item-id-for-an-arcgis-online-item) from Esri has more information.
Set the ```fcId``` variable in ```main()``` to the feature ID of your table.

## Setting up the feature services in AGOL
1. Set up the data sources
With your ArcGIS Online account, you'll need:
* A table that matches the dataframe's output. I would recommend just [downloading the daily.csv](https://api.covidtracking.com/v1/states/current.csv) from COVIDTracking.com and uploading that as a table. This will be referred to as the **covidtracking table**
* A feature class of the US states with a ```state_abbr``` field. There's plenty out there. This will be referred to as the **states feature class**
You'll need ownership of both the table and the feature class.

2. Set up the joined feature
   1. In an empty web map, add both the **covidtracking table** and the **states feature class**. 
   2. Select "Analytics" in the top left corner.
   3. Select "Join Features" from the "Summarize Data" group.
   4. In "Join Features":
    1. select the **states feature class** as the target layer
    2. select the **covidtracking table** as the layer to join to target layer
    3. select *fields* as the type of join. In *fields*, choose the ```[state]``` field and whatever the ```[state_abbr]``` field is for your feature class.
    4. For choose join operation:
       * If this is a 'current' dataset, select Join 1:1. Define the record using Order By ```valid```, and sort by Newest.
       * If this will be a timeseries, select Join 1:M.
    5. Give the result layer a name
    6. Uncheck Use Current Map Extent, and select Create results as hosted feature layer view. This will make sure that whenever you update the table, the feature layer will also update without you having to do the join every time.
    7. Run the analysis!

3. Make some cool maps and dashboards!

# Disclaimer
This project is primarily meant as a portfolio to show some of my skills as a programmer. By the time you read this, the script may no longer work. I've linked to a dashboard I built to show how this data looked when I last ran the script. I've also decided that it would be better for the GIS products to show information for when there was a significant amount of COVID activity, and I hope by the time you read this that will no longer be the case.

A similar script I had built for my day job has been running since early March and by late August has saved my team over 500 hours of manually searching for data and entering it into a GIS compatable system.
