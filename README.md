# Welcome to My AWS PlayGround

***aws_bill_notifications_lambda.py***

This python lambda function periodically sends you billing notifications.

    AWS Account
    
    Yesterday Usage : Kshs. 730
    
    Month To Date Bill : Kshs. 12,640
    
    Forecasted Bill : Kshs. 20,479

This helps you keep track of your AWS spending in order to avoid surprises at the end of the month

**How It Works**

It uses cost explorer APIs to get your bill details and then sends them using SNS.

**IAM Permissions Required**
 - cost explorer
 - sns

**How to set it up**

 - Create a python lambda function
 - Initialize the environment variables
 - Schedule the lambda function to run periodically using CloudWatch events

**Lambda Environment Variables**

 - currency : name of your local currency e.g kshs
 - dollar_exchange_rate  : the function converts from dollars to your local currency
 - sns_topic : arn of your sns topic
 - subject : subject of the message that is sent
 




***Codepipline that pushes code to cpanel on repository commit***

![enter image description here](https://rentrahisi.co.ke/myimages/pipeline.jpg)

 1. Set up codebuild to build your code once a commit is made to your repository. You can also use codebuild to run your tests. When building is complete, the code is stored in s3
 2. Create a codepipeline that will trigger automatically when you push a commit to your repository ( bitbucket, github, codecommit etc). The first stage will be your code source and the second stage will be codebuild.
 3. When you push a commit, the pipeline will run. The code will be built and stored in S3. You can set up an S3 lifecyle rule to delete old code artifacts. You can also set up a CloudWatch event rule that will inform you via SNS of the state of the pipeline execution ( successful or failed ).
 4. The code now needs to be pushed to cpanel. Set up an S3 events that monitors for new object creation. When code is pushed, set the event to invoke a lambda function.
 5. The Lambda will fetch the code from S3 and store it in its /tmp directory which is limited to 512 mb. The lambda will unzip the code and push it to cpanel using FTP. FTP credentials are fetched from the AWS Parameter Store. Lambda can then inform you via SNS when the code has been successfully pushed. Lambda has a maximum running time of 15 minutes. 

***lambda - codepipeline_cpanel_push_lambda.py***

**IAM Permissions Required**
 - cloudwatch
 - S3
 - SNS
 - SSM

**Lambda Environment Variables**

 - bucket: bucket name for bucket that stores codepipeline artifacts
 - ftp_hostname
 - sns_topic : arn of sns topic to send you a notification when code has been pushed to cpanel
 - region

***Benefits**

 - Enforces GitOps
 - Code backup
 - Code sharing
 - Easy rollback in case of a bad commit

**Cost of the solution**

 - Codepipeline - $1 per month per active pipeline
 - Codebuild - $0.05 per build minute ( using 3 GB Mem and 2 vCPU)
 - S3 - $0.023 per GB
 - Cloudwatch logs - $0.57 per GB
 - Cloudwatch events - $1.00 per million events












