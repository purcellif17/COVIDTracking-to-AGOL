# pylint: disable=E1101
# Pylint doesn't like the arcgis module for one reason or another

from arcgis import GIS
from datetime import datetime
import os
import json
import logging

fileLocation = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(filename='logs.log',filemode='a',format='%(asctime)s | %(lineno)s | %(levelname)s | %(message)s',level=logging.INFO)

def covidTrackingAPI():
    try:
        import requests
        logging.info('Getting data from CovidTracking.com...')
        tracking_API = 'https://covidtracking.com//api//v1//states//daily.json'
        covidTracking = requests.get(tracking_API).json()

        return covidTracking

    except Exception:
        logging.error("There was an error retrieving data from COVIDTracking.com", exc_info=True)

def tableProcessing(api):
    try:
        import pandas as pd

        logging.info('Preparing the data for AGOL...')
        df = pd.read_json(json.dumps(api))
        df = df.sort_values(by=['date'], ascending=True)

        df['dailyPos'] = df.groupby('state')['positive'].apply(lambda x: x-x.shift(1))
        df['dailyNeg'] = df.groupby('state')['negative'].apply(lambda x: x-x.shift(1))
        df['dailyTot'] = df.groupby('state')['totalTestResults'].apply(lambda x: x-x.shift(1))

        df['pctPos'] = (df['dailyPos']/df['dailyTot'])*100
        df['pctPosCum'] = (df['positive']/df['totalTestResults'])*100

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

    except Exception:
        logging.error("There was an error calculating data.", exc_info=True)

def buildUpdates(lyr,filtered_json,current_data):
    try:
        add_features = []
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
            if valid not in current_data:
                add_features.append(f)
            else:
                update_features.append(f)
        return add_features, update_features
    except Exception:
        logging.error('There was an error bulding the field map', exc_info=True)

def main():
    
    # Start counter
    dtStart = datetime.now()
    logging.info("Initiating {}\n".format(__file__))
    # Call the API
    api = covidTrackingAPI()

    # Process the table
    filtered_json = tableProcessing(api)
    try:
        # Create the GIS connection
        gis = GIS(profile='AGOL')
        logging.info("logged in as {}".format(gis.users.me.username))
        logging.info("Getting layer from AGOL")

        # Variable for the hosted feature service ID, modify if the hosted feature service changes
        fcId = 'fa8f69c34bc8418cad7ba9e0cfa6b568'

        # Load the cases table from AGOL
        table = gis.content.get(fcId).tables[0]
    except Exception:
        logging.error('There was an error accessing the feature on AGOL.', exc_info=True)

    try:
        #Commit the edits to the feature service
        logging.info("Getting updated features")
        # Removes previous records since data is updated retroactively
        query = table.query(where='1=1',return_geometry=False,out_fields='*')
        current_data = []
        for attribute in query:
            date = datetime.fromtimestamp((attribute.attributes['valid']/1000))
            if date not in current_data:
                current_data.append(date)

        add_features, update_features = buildUpdates(table,filtered_json,current_data)

        logging.info("Appending {} new records".format(len(add_features)))
        table.edit_features(adds=add_features)
        logging.info("Updating {} records".format(len(update_features)))
        table.edit_features(updates=update_features)

        logging.info("All data updated")
    except Exception:
        logging.error('There was an error appending the data to the table on AGOL.', exc_info=True)
        print(Exception)
    script_run = datetime.now() - dtStart
    logging.info("Script run time: {}".format(script_run))
    logging.info("SCRIPT COMPLETE\n")

main()
