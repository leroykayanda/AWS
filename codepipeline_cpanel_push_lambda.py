from ftplib import FTP 
import os
import fileinput
import json
import boto3
from zipfile import ZipFile

def lambda_handler(event, context):
    # get environment variables
    
    region=os.environ['region']
    bucket=os.environ['bucket']
    sns_topic=os.environ['sns_topic']
    ftp_hostname=os.environ['ftp_hostname']
    ftp_directory=os.environ['ftp_directory']
    
    # get S3 object key from event
    zip_file=event["Records"][0]["s3"]["object"]["key"]
    
    #get code from s3 and store it in /tmp directory of lambda
    s3 = boto3.resource('s3')
    s3.Object(bucket, zip_file).download_file('/tmp/zipped')
    
    #unzip code into /tmp/unzipped
    zip = ZipFile("/tmp/zipped")
    zip.extractall("/tmp/unzipped")
    zip.close()
    
    #get FTP Logins from parameter store
    ssm=boto3.client('ssm',region_name=region)
    godaddy_logins=ssm.get_parameters(Names=["godaddy_username","godaddy_password"], WithDecryption=True)
    
    logins =godaddy_logins["Parameters"]
    godaddy_password=logins[0]["Value"]
    godaddy_username=logins[1]["Value"]
    
    ftp = FTP()
    ftp.set_debuglevel(2)
    ftp.connect(ftp_hostname, 21) 
    ftp.login(godaddy_username, godaddy_password)
    ftp.cwd(ftp_directory)
    
    path = '/tmp/unzipped'
    
    upload(ftp,path)
    
    client = boto3.client('sns')
    msg="Lambda execution complete"
    
    response = client.publish(
    TopicArn=sns_topic,
    Message=msg,
    Subject="RentRahisi Code Pushed to GoDaddy"
    )

def upload(ftp,path):
	for name in os.listdir(path):
		localpath = os.path.join(path, name)
		
		if os.path.isfile(localpath):
			fp = open(localpath, 'rb')
			ftp.storbinary('STOR %s' % os.path.basename(localpath), fp, 1024)
			fp.close()
		elif os.path.isdir(localpath):
			try:
				ftp.mkd(name)
				
			# ignore "directory already exists"
			except Exception:
				print(name+" exists already")
				
			ftp.cwd(name)
			upload(ftp,localpath)
			print("Going back 1 step")
			ftp.cwd("..")
	
