from watson_machine_learning_client import WatsonMachineLearningAPIClient
import math
import PIL
from PIL import Image
import numpy as np
from flask import Flask, request, json, jsonify
import os
import urllib3, requests, json

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
ENDPOINT_URL =  \
    "https://us-south.ml.cloud.ibm.com/v4/deployments/1af73655-d02f-4801-864d-04b1b364c154/predictions";

def createPayload( canvas_data ):
    payload_list   = payload_arr.tolist()
    return { "values" : payload_list }

def get_samp_payload():
    eq_primary = 7
    population = 21_000_000
    payload_scoring = {"input_data": [{"fields": ["EQ_PRIMARY", "POPULATION"], "values": [[eq_primary, population]] }]}
    return payload_scoring


app = Flask( __name__, static_url_path='' )

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int( os.getenv( 'PORT', 8000 ) )

@app.route('/dummy_test')
def dummy_test():

    import urllib3, requests, json

    # NOTE: generate iam_token and retrieve ml_instance_id based on provided documentation	
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + iam_token, 'ML-Instance-ID': wml_credentials['instance_id']}

    # NOTE: manually define and pass the array(s) of values to be scored in the next line

    payload = get_samp_payload()

    response_scoring = requests.post(ENDPOINT_URL, json=payload_scoring, headers=header)
    print("Scoring response")
    out = json.loads(response_scoring.text)
    print(out)
    return response_scoring.text;



    # payload = get_samp_payload()
    # result = client.deployments.score( model_deployment_endpoint_url, payload )
    # print( "result: " + json.dumps( result, indent=3 ) )
    # return jsonify( result )


@app.route('/')
def root():
    return app.send_static_file( 'index.html' )

@app.route( '/send', methods=['GET', 'POST'] )
def send():
    try:
        print( "sending..." )
        if ENDPOINT_URL:
            payload = get_samp_payload()
            result = client.deployments.score( ENDPOINT_URL, payload )
            print('result: ' + json.dumps( result, indent=3 ))
            prediction = result['predictions'][0]['values'][0][0]
            print(f'prediction: {prediction}')
            return jsonify( result )
        else:
            err = "endpoint URL not set in 'server.py'"
            print( "\n\nError:\n" + err )
            return jsonify( { "error" : err } )
    except Exception as e:
        print( "\n\nError:\n" + str( e ) )
        return jsonify( { "error" : str( e ) } )

if __name__ == '__main__':
    app.run( host='0.0.0.0', port=port, debug=True)
