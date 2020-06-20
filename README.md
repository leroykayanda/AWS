# Welcome to My Collection of AWS Lambda Functions

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

 1. Create a python lambda function
 2. Add the environment variables : sns_topic and subject. sns_topic is the ARN of the sns topic to send notifications to. subject is the subject of the message with your billing details
 3. Schedule the lambda function to run periodically using CloudWatch events



