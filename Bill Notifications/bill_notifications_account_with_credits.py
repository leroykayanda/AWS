import boto3
import json
from datetime import datetime, timedelta
from dateutil import relativedelta
import os
import urllib3
http = urllib3.PoolManager()
import datetime as dt
import calendar

dollar_exchange_rate = float(os.environ['dollar_exchange_rate'])
client = boto3.client('ce')


def lambda_handler(event, context):
    sendEmail()
    # return predictedBill()


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
            'NET_UNBLENDED_COST'
        ],
        Filter={
            'Not': {
                'Or': [
                    {
                        'Dimensions': {
                            'Key': 'RECORD_TYPE',
                            'Values': [
                                'Credit'
                            ]
                        }
                    },
                    {
                        'Dimensions': {
                            'Key': 'RECORD_TYPE',
                            'Values': [
                                'Refund'
                            ]
                        }
                    }
                ]
            }
        }
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
            'NET_UNBLENDED_COST'
        ],
        Filter={
            'Not': {
                'Or': [
                    {
                        'Dimensions': {
                            'Key': 'RECORD_TYPE',
                            'Values': [
                                'Credit'
                            ]
                        }
                    },
                    {
                        'Dimensions': {
                            'Key': 'RECORD_TYPE',
                            'Values': [
                                'Refund'
                            ]
                        }
                    }
                ]
            }
        }
    )

    yesterdays_bill = round(float(
        response["ResultsByTime"][0]["Total"]["NetUnblendedCost"]["Amount"]))*dollar_exchange_rate

    #print("Yesterday: " + str(yesterdays_bill))
    return yesterdays_bill


def predictedBill():

    today = dt.date.today()
    start_date = datetime.strftime( today, '%Y-%m-%d' )
    end_date = datetime.strftime( dt.date(today.year, today.month+1, 1), '%Y-%m-%d' )
    
    response = client.get_cost_forecast(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Metric='NET_UNBLENDED_COST',
        Granularity='MONTHLY',
        Filter={
            'Not': {
                'Or': [
                    {
                        'Dimensions': {
                            'Key': 'RECORD_TYPE',
                            'Values': [
                                'Credit'
                            ]
                        }
                    },
                    {
                        'Dimensions': {
                            'Key': 'RECORD_TYPE',
                            'Values': [
                                'Refund'
                            ]
                        }
                    }
                ]
            }
        }
    )

    predicted = round(
        float(response['Total']['Amount']) * dollar_exchange_rate)

    #print("Predicted: " + str(predicted))
    return predicted


def sendEmail():
    currency = os.environ['currency']
    client = boto3.client('sns')
    
    msg = "AWS Bill\n\nYesterday Usage : "+currency+" " + format(int(getYesterdayBill()), ',d') + " \n\nMonth To Date Bill : "+currency+" " + format(
        int(getMonthBill()), ',d') + " \n\nForecasted Bill : "+currency+" " + format(int(predictedBill()), ',d')

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


# sendEmail()
# export currency = "$"
# export dollar_exchange_rate = 1
# export slack_webhook="https://hooks.slack.com/services/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"
# export subject = "AWS Bill"
