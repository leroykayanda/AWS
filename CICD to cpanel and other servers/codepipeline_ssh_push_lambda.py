#!/usr/bin/env python3

import pysftp
import os
import boto3
from zipfile import ZipFile
import sys
import time

s3 = boto3.resource('s3')
client = boto3.client('sns')


def lambda_handler(event, context):
    region = os.environ['region']
    bucket = os.environ['bucket']
    sns_topic = os.environ['sns_topic']
    target_host = os.environ['target_host']
    target_directory = os.environ['target_directory']
    zipped_src = os.environ['zipped_src']
    unzipped_src = os.environ['unzipped_src']

    # get S3 object key from event
    zip_file = event["Records"][0]["s3"]["object"]["key"]

    s3.Object(bucket, zip_file).download_file(zipped_src)

    # unzip code into /tmp/unzipped
    zip = ZipFile(zipped_src)
    zip.extractall(unzipped_src)
    zip.close()

    # get SSH Logins from parameter store
    ssm = boto3.client('ssm', region_name=region)
    server_logins = ssm.get_parameters(
        Names=["lightsail_username", "lightsail_password"], WithDecryption=True)

    logins = server_logins["Parameters"]
    passw = logins[0]["Value"]
    user = logins[1]["Value"]

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(host=target_host, username=user, password=passw, cnopts=cnopts) as sftp:
        print("SFTP connection established ... ")

        # cd to the destination of the upload
        sftp.cwd(target_directory)
        upload(unzipped_src, sftp)

    # send notification upload is complete
    msg = "Lambda execution complete"

    response = client.publish(
        TopicArn=sns_topic,
        Message=msg,
        Subject="Code Pushed to Server"
    )


def upload(path, sftp):
    for name in os.listdir(path):
        localpath = os.path.join(path, name)

        if os.path.isfile(localpath):
            # file
            sftp.put(localpath)
        elif os.path.isdir(localpath):
            # dir
            try:
                sftp.mkdir(name)
            # ignore "directory already exists"
            except Exception:
                print(name+" exists already")
                #print("Oops!", sys.exc_info()[0], "occurred.")
            # print(name)
            sftp.cwd(name)
            upload(localpath, sftp)
            print("Going back 1 step")
            sftp.cwd('..')
