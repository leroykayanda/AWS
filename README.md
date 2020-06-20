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

 - Create a python lambda function
 - Initialize the environment variables
 - Schedule the lambda function to run periodically using CloudWatch events

**Environment Variables**

 - currency : name of your local currency e.g kshs
 - dollar_exchange_rate  : the function converts from dollars to your local currency
 - sns_topic : arn of your sns topic
 - subject : subject of the message that is sent





