
import urllib3
import json
http = urllib3.PoolManager()
import gzip
import base64
import boto3
import datetime
import os

url= os.environ['slack_webhook']

def lambda_handler(event, context):
   
    #print(event)
    
    #get log event
    cloudwatch_event= event['awslogs']['data']

    #log event is encoded using vase 64. decode it
    decoded_event=base64.b64decode(cloudwatch_event)

    #log events is compressed. unzip it
    decompressed_event=gzip.decompress(decoded_event)

    #convert JSON string to python dictionary
    log_data=json.loads(decompressed_event)

    #extract event from the dictionary
    event=json.loads( log_data['logEvents'][0]['message'] )
    print(event)
    
    userType = event['userIdentity']['type']
    eventTime = event['eventTime']
    sourceIPAddress = event['sourceIPAddress']
    
    if userType == 'Root':
        msg = "The root user has logged in to the AWS console without MFA at " + eventTime + " from IP " + sourceIPAddress + ". Please follow <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa_enable_virtual.html | this guide> to set up MFA."
    else:
        userName = event['userIdentity']['userName']
        msg = userName + " has logged in to the AWS console without MFA at " + eventTime + " from IP " + sourceIPAddress + ". Please follow <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa_enable_virtual.html | this guide> to set up MFA."
    
    #print(msg)
    
    msg = {
        "text": msg,
    }
    
    encoded_msg = json.dumps(msg).encode('utf-8')
    
    resp = http.request('POST',url, body=encoded_msg)
    print({
        "message": msg, 
        "status_code": resp.status, 
        "response": resp.data
    })
    
    