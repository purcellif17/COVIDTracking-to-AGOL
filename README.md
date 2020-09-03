# COVIDTracking.com-to-AGOL

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
