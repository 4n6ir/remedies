import boto3
import json
import os
from boto3.dynamodb.conditions import Key
from decimal import Decimal

def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

def handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
    response = table.query(KeyConditionExpression=Key('pk').eq('AWS#') & Key('sk').begins_with('SERVICE#'))
    responsedata = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.query(
            KeyConditionExpression=Key('pk').eq('AWS#') & Key('sk').begins_with('SERVICE#'),
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        responsedata.update(response['Items'])
    

    return {
        'statusCode': 200,
        'body': json.dumps(responsedata, default=default)
    }
