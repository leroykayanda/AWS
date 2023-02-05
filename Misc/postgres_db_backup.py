#!/usr/bin/env python3

import subprocess
from datetime import datetime
import sys
import urllib3
import json
http = urllib3.PoolManager()
import boto3
from botocore.exceptions import ClientError
import os
import time

#sys.exit()
session = boto3.Session(
    region_name="eu-west-1"
)
secrets_client = session.client("secretsmanager")
s3_client = session.client("s3")
cloudwatch_client = session.client("logs")

now = datetime.now()
date_string = now.strftime("%Y-%m-%d-%H-%M-%S")

app = sys.argv[1]
filename = app + '-backup-' + date_string + '.sql'
db_name = sys.argv[2]
db_host = 'db.bit.io'
slack_webhook = sys.argv[3]
secret_arn = sys.argv[4]
bucket = sys.argv[5]
logGroupName = sys.argv[6]
logStreamName = sys.argv[7]

def send_slack(message):
    msg = {
        "text": message
    }
    
    encoded_msg = json.dumps(msg).encode('utf-8')

    resp = http.request('POST',slack_webhook, body=encoded_msg)

def upload_file_to_s3():
    try:
        object_name = app + "/" + filename
        response = s3_client.upload_file(filename, bucket, object_name)
    except boto3.exceptions.S3UploadFailedError as e:
        error = 'Error backing up '+ db_name + ' database \n\n' + str(e)
        print(error)
        send_slack(error)
        sys.exit()

    #delete the file
    if os.path.exists(filename):
        os.remove(filename)
    return True

def get_db_credentials():
    response = secrets_client.get_secret_value(
        SecretId = secret_arn
        )

    SecretString = json.loads(response['SecretString'])
    res = {}
    res["DB_USER"] = SecretString['DB_USER']
    res["DB_PASSWORD"] = SecretString['DB_PASSWORD']
    return res

def perform_backup():
    db_credentials = get_db_credentials()
    DB_USER = db_credentials['DB_USER']
    DB_PASSWORD = db_credentials['DB_PASSWORD']

    os.environ["PGPASSWORD"] = DB_PASSWORD

    result = subprocess.run(['pg_dump', '-h', db_host, '-U', DB_USER, '-F', 'p', db_name,'-f',filename],stderr=subprocess.PIPE )
    
    if result.returncode != 0:
        error = 'Error backing up '+ db_name + ' database \n\n' + result.stderr.decode() 
        print(error)
        #send error to slack
        send_slack(error)
        sys.exit()

def save_to_cloudwatch(): 
    timestamp_milliseconds = int(time.time() * 1000)
    msg = db_name + 'database backed up'

    response = cloudwatch_client.put_log_events(
        logGroupName=logGroupName,
        logStreamName=logStreamName,
        logEvents=[
            {
                'timestamp': timestamp_milliseconds,
                'message': msg
            }
            ]
        )

perform_backup()
upload_file_to_s3()
save_to_cloudwatch()