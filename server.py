from watson_machine_learning_client import WatsonMachineLearningAPIClient
import math
import PIL
from PIL import Image
import numpy as np
from flask import Flask, request, json, jsonify
import os
import urllib3, requests, json
import traceback

# access the FCC's and Census Bureau data through an API
import census_data

# the ai isn't effective at estimating injuries when the population is very low
POP_CUTOFF = 2_000

#
# 1.  Fill in wml_credentials.
#

#apikey = "DVkMuQdBKICKJrrWoRY_u-tpH1A_ixaiSoMB-XKH-fsT"

wml_credentials = {
  "apikey": "mAcWVA-89GKeXQFaWdOJMtg5FLyU3D6xKj4k5iKW105M",
  "iam_apikey_description": "Auto-generated for key abf05a66-5dea-4eca-8c28-dd9683828c23",
  "iam_apikey_name": "wdp-writer",
  "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Writer",
  "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::a/e65d048fcf3c47b694773e2bbe215f05::serviceid:ServiceId-17c7dcf0-c5d0-474d-92b9-6ad0b0863f6c",
  "instance_id": "6bde0f46-f4e8-4f1f-adf6-e11b142f27dc",
  "url": "https://us-south.ml.cloud.ibm.com"
}
apikey = wml_credentials['apikey']

def get_iam_token(): 
    url     = "https://iam.bluemix.net/oidc/token"
    headers = { "Content-Type" : "application/x-www-form-urlencoded" }
    data    = "apikey=" + apikey + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
    IBM_cloud_IAM_uid = "bx"
    IBM_cloud_IAM_pwd = "bx"
    response  = requests.post( url, headers=headers, data=data, auth=( IBM_cloud_IAM_uid, IBM_cloud_IAM_pwd ) )
    iam_token = response.json()["access_token"]
    return iam_token



client = WatsonMachineLearningAPIClient( wml_credentials )
iam_token = get_iam_token()

#
# 2.  Fill in one or both of these:
#     - model_deployment_endpoint_url
#     - function_deployment_endpoint_url
#
#model_deployment_endpoint_url    = "https://us-south.ml.cloud.ibm.com/v4/deployments/1af73655-d02f-4801-864d-04b1b364c154/predictions";
#function_deployment_endpoint_url = "https://us-south.ml.cloud.ibm.com/v4/deployments/1af73655-d02f-4801-864d-04b1b364c154/predictions";
INJURIES_ENDPOINT_URL =  \
    "https://us-south.ml.cloud.ibm.com/v4/deployments/1af73655-d02f-4801-864d-04b1b364c154/predictions"
DAMAGES_ENDPOINT_URL = \
    "https://us-south.ml.cloud.ibm.com/v4/deployments/50665275-98f7-4ee9-a458-b044a9cd2251/predictions"

def create_payload_injuries(magnitude, population): 
    payload_scoring = {
        "input_data": [{
            "fields": ["EQ_PRIMARY", "POPULATION"],
            "values": [[magnitude, population]]
            }]
    }
    return payload_scoring

def create_payload_damages(magnitude, population):
    payload_scoring = {
        "input_data": [{
            "fields": ["Year", "EQ_PRIMARY", "POPULATION"],
            "values": [[2019, magnitude, population]]
            }]
    }
    return payload_scoring

app = Flask( __name__, static_url_path='' )

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int( os.getenv( 'PORT', 8000 ) )



@app.route('/')
def root():
    return app.send_static_file( 'index.html' )

@app.route( '/send', methods=['GET', 'POST'] )
def send():
    try:
        print( f"sending..." )
        if INJURIES_ENDPOINT_URL and DAMAGES_ENDPOINT_URL:
            # determine what type of info needs to be retrieved
            is_injuries = request.args['injuries']
            # parse the magnitude and location
            magnitude = request.args['magnitude']
            #print(f"{magnitude}")
            lat, lng = request.args['location'].split(',')
            lng = lng.strip()
            # look up census data at that region
            pop = census_data.get_population(lat, lng)
            #print(f"population: {pop}peeps")

            result = {'warn_msg': ''}
            if pop is None:
                warn_msg = "no population data at specified geolocation"
                pop = 0
            elif pop < POP_CUTOFF and pop != 0:
                warm_msg = f"population size is small: {pop} < {POP_CUTOFF} and estimations will be imprecise"
            
            if pop == 0:
                result['injuries'] = 0
                result['damages'] = 0
                return jsonify( result )

            # CALCULATE EXPECTED INJURY COUNT
            injury_payload = create_payload_injuries(magnitude, pop)
            # query the IBM watson AutoAI
            result['injuries'] = client.deployments.score( INJURIES_ENDPOINT_URL, injury_payload )['predictions'][0]['values'][0][0]
            
            # CALCULATE EXPECTED DAMAGES COST
            damages_payload = create_payload_damages(magnitude, pop)
            # query the IBM watson AutoAI
            result['damages'] = client.deployments.score( DAMAGES_ENDPOINT_URL, damages_payload )['predictions'][0]['values'][0][0]
            
            print(result)
            # return the result
            return jsonify( result )
        else:
            err = "endpoint URL not set in 'server.py'"
            print( "\n\nError:\n" + err )
            return jsonify( { "error" : err } )
    except Exception as e:
        print( "\n\nError:\n" + traceback.format_exc() )
        print( "")
        return jsonify( { "error" : str( e ) } )

if __name__ == '__main__':
    app.run( host='0.0.0.0', port=port, debug=True)
