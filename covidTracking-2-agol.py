# pylint: disable=E1101
# Pylint doesn't like the arcgis module for one reason or another

from arcgis import GIS
from datetime import datetime
import os
import json
import configparser
import logging.config

fileLocation = os.path.abspath(os.path.dirname(__file__))

def covidTrackingAPI():
    import requests

    print('Getting data from CovidTracking.com...')
    tracking_API = 'https://covidtracking.com//api//v1//states//daily.json'
    covidTracking = requests.get(tracking_API).json()

    return covidTracking

def tableProcessing(api):
    import pandas as pd

    print('Preparing the data for AGOL...')
    df = pd.read_json(json.dumps(api))
    df = df.sort_values(by=['date'], ascending=True)

    df['dailyPos'] = df.groupby('state')['positive'].apply(lambda x: x-x.shift(1))
    df['dailyNeg'] = df.groupby('state')['negative'].apply(lambda x: x-x.shift(1))
    df['dailyTot'] = df.groupby('state')['total'].apply(lambda x: x-x.shift(1))

    df['pctPos'] = (df['dailyPos']/df['dailyTot'])*100
    df['pctPosCum'] = (df['positive']/df['total'])*100

    df['tot7day'] = df.groupby('state')['dailyTot'].apply(lambda x: x.rolling(7,1).sum())
    df['avgTest7day'] = df.groupby('state')['dailyTot'].apply(lambda x: x.rolling(7,1).mean())
    df['pos7day'] = df.groupby('state')['dailyPos'].apply(lambda x: x.rolling(7,1).sum())
    df['pctPos7day'] = (df['pos7day']/df['tot7day'])*100
    df['hospitalizedChange'] = df.groupby('state')['hospitalizedCurrently'].apply(lambda x: x-x.shift(1))
    df['hospitalized7day'] = df.groupby('state')['hospitalizedChange'].apply(lambda x: x.rolling(7,1).mean())

    df['avgTest2wkAgo'] = df.groupby('state')['avgTest7day'].apply(lambda x: x.shift(14))
    df['pctPos2wkAgo'] = df.groupby('state')['pctPos7day'].apply(lambda x: x.shift(14))

    filtered_json = json.loads(df.to_json(orient='table'))

    return filtered_json

def updateFeatures(lyr,filtered_json):

    update_features = []

    for field in filtered_json['data']:
        valid = datetime.strptime(str(field['date']),'%Y%m%d')
        attributes = {
            'state': field['state'],
            'dataQualityGrade': field['dataQualityGrade'],
            'death': field['death'],
            'deathConfirmed': field['deathConfirmed'],
            'deathIncrease': field['deathIncrease'],
            'deathProbable': field['deathProbable'],
            'hospitalized': field['hospitalized'],
            'hospitalizedCumulative': field['hospitalizedCumulative'],
            'hospitalizedCurrently': field['hospitalizedCurrently'],
            'hospitalizedChange': field['hospitalizedChange'],
            'hospitalized7day': field['hospitalized7day'],
            'inIcuCumulative': field['inIcuCumulative'],
            'inIcuCurrently': field['inIcuCurrently'],
            'negative': field['negative'],
            'dailyNeg': field['dailyNeg'],
            'onVentilatorCumulative': field['onVentilatorCumulative'],
            'onVentilatorCurrently': field['onVentilatorCurrently'],
            'pending': field['pending'],
            'positive': field['positive'],
            'positiveScore': field['positiveScore'],
            'dailyPos': field['dailyPos'],
            'pctPos': field['pctPos'],
            'pctPosCum': field['pctPosCum'],
            'pctPos7day': field['pctPos7day'],
            'pctPos2wkAgo': field['pctPos2wkAgo'],
            'recovered': field['recovered'],
            'totalTestResults': field['totalTestResults'],
            'totalTestResultsIncrease': field['totalTestResultsIncrease'],
            'dailyTot': field['dailyTot'],
            'avgTest7day': field['avgTest7day'],
            'avgTest2wkAgo': field['avgTest2wkAgo'],
            'valid': valid
        }

        f = {
            'attributes': attributes
        }
        update_features.append(f)
    return update_features

def main():
    # Start counter
    dtStart = datetime.now()

    # Call the API
    api = covidTrackingAPI()

    # Process the table
    filtered_json = tableProcessing(api)

    # Create the GIS connection
    gis = GIS(profile='AGOL')
    print("logged in as {}".format(gis.users.me.username))

    print("Getting layer from AGOL")

    # Variable for the hosted feature service ID, modify if the hosted feature service changes
    fcId = 'fa8f69c34bc8418cad7ba9e0cfa6b568'

    # Load the cases table from AGOL
    table = gis.content.get(fcId).tables[0]

    tableCases = updateFeatures(table,filtered_json)

    #Commit the edits to the feature service
    print("Appending updated features")
    # Removes previous records since data is updated retroactively
    table.manager.truncate()
    table.edit_features(adds=tableCases)

    print("All data updated")
    script_run = datetime.now() - dtStart
    print("Script run time: {}".format(script_run))
    print("SCRIPT COMPLETE")

main()
