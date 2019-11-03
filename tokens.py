import urllib3, requests, json

#
# 1.  Fill in wml_credentials.
#

apikey = "DVkMuQdBKICKJrrWoRY_u-tpH1A_ixaiSoMB-XKH-fsT"

wml_credentials = {
  "apikey": apikey,
  "iam_apikey_description": "Auto-generated for key e7242d15-9fbc-4996-b683-c153edd8c52e",
  "iam_apikey_name": "Service credentials-2",
  "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Manager",
  "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::a/c1985321d74a498fa578033c2f7dbdbf::serviceid:ServiceId-62482c20-b99f-4e46-b378-0f0b23cd1a5a",
  "instance_id": "7ea9b45b-656f-41fb-a621-91229e8a7f3b",
  "url": "https://us-south.ml.cloud.ibm.com"
}

url     = "https://iam.bluemix.net/oidc/token"
headers = { "Content-Type" : "application/x-www-form-urlencoded" }
data    = "apikey=" + apikey + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
IBM_cloud_IAM_uid = "bx"
IBM_cloud_IAM_pwd = "bx"
response  = requests.post( url, headers=headers, data=data, auth=( IBM_cloud_IAM_uid, IBM_cloud_IAM_pwd ) )
iam_token = response.json()["access_token"]

print(f"iam_token: {iam_token}")