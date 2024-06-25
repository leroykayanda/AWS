import boto3
import json
from datetime import datetime, timedelta
from dateutil import relativedelta
import os
import urllib3
http = urllib3.PoolManager()
import datetime as dt
import calendar

dollar_exchange_rate=float( os.environ['dollar_exchange_rate'] )
client = boto3.client('ce')

def lambda_handler(event, context):  
    sendEmail()
    #return getYesterdayBill()
    
def getMonthBill():

    today = datetime.today()
    start_date = datetime.strftime(today + relativedelta.relativedelta(day=1), '%Y-%m-%d')
    end_date = datetime.strftime(datetime.now() + timedelta(1), '%Y-%m-%d')

    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=[
            'NetUnblendedCost'
        ]
    )

    month_to_date_bill = round(float(
        response["ResultsByTime"][0]['Total']["NetUnblendedCost"]["Amount"]) * dollar_exchange_rate)
    #print("To date: " + str(month_to_date_bill))
    return month_to_date_bill


def getYesterdayBill():
    
    start_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
    #print(start_date)
    
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=[
            'NetUnblendedCost'
        ]
    )

    yesterdays_bill = round(float(
        response["ResultsByTime"][0]["Total"]["NetUnblendedCost"]["Amount"]))*dollar_exchange_rate

    #print("Yesterday: " + str(yesterdays_bill))
    return yesterdays_bill


def predictedBill():

    today = dt.date.today()
    start_date = datetime.strftime( today, '%Y-%m-%d' )
    
    month = today.month+1
    year = today.year
    
    if(month == 13):
        #if in Dec, set end date to be 1st Jan of the next year
        month = 1
        year += 1
    
    end_date = datetime.strftime( dt.date(year, month, 1), '%Y-%m-%d' )
    
    response = client.get_cost_forecast(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Metric='NetUnblendedCost',
        Granularity='MONTHLY'
    )

    predicted = round(
        float(response['Total']['Amount']) * dollar_exchange_rate)

    #print("Predicted: " + str(predicted))
    return predicted
    
def sendEmail():
    currency=os.environ['currency']
    
    client = boto3.client('sns')
    msg="AWS Personal Account\n\nYesterday Usage : "+currency+" "+ format( int( getYesterdayBill() ) ,',d' ) +" \n\nMonth To Date Bill : "+currency+" "+ format( int( getMonthBill() )  ,',d' )  +" \n\nForecasted Bill : "+currency+" "+ format( int( predictedBill() )  ,',d' ) 
    
    sns_topic=os.environ['sns_topic']
    subject=os.environ['subject']
	
    response = client.publish(
    TopicArn=sns_topic,
    Message=msg,
    Subject=subject
    )
    
def send_slack_msg():
    
    msg = "AWS Bill\n\nYesterday Usage : "+currency+" " + format(int(getYesterdayBill()), ',d') + " \n\nMonth To Date Bill : "+currency+" " + format(
        int(getMonthBill()), ',d') + " \n\nForecasted Bill : "+ predictedBill()

    slack_webhook = os.environ['slack_webhook']

    print(msg)

    msg = {
        "text": msg
    }

    encoded_msg = json.dumps(msg).encode('utf-8')
    
    resp = http.request('POST', slack_webhook, body=encoded_msg)
    print({
        "message": msg,
        "status_code": resp.status,
        "response": resp.data
    })