import json
import boto3
from boto3.dynamodb.conditions import Key

db_obj = boto3.resource('dynamodb')
table = db_obj.Table('<table>')

def operation_scan():
    # デーブルスキャン
    scanData = table.scan()
    items = scanData['Items']
    #print(items)
    return sorted(items, key=lambda x: x['date'])

def lambda_handler(event, context):
    # TODO implement
    print('Received event:', json.dumps(event))
    operation_type = event['operation']
    try:
        print('a')
        data = None
        if operation_type == 'all':
            data = operation_scan()
    except Exception as e:
        print('エラー')
        print(e)
        
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': 'https://group5.a2136km.com/',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': data
    }
