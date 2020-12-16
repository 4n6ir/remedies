### https://awspolicygen.s3.amazonaws.com/policygen.html ###

import boto3
import datetime
import json
import logging
import os
import urllib.request

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(event)
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
    orig = datetime.datetime.now()
    new = orig + datetime.timedelta(days=33)
    
    url = 'https://awspolicygen.s3.amazonaws.com/js/policies.js'
    with urllib.request.urlopen(url) as response:
        output = response.read()
    response.close()
    with open('/tmp/policies.js', 'wb') as f:
        f.write(output)
    f.close()
    
    f = open('/tmp/policies.js','r')
    reading = f.readline()
    output = reading.split('HasResource')
    output = output[1:-1]
    for item in output:
        parsedstart = item.split('[')
        named = parsedstart[0].split(':')
        longname = named[1].split('"')
        thelongname = longname[1]
        shortname = named[3].split('"')
        theshortname = shortname[1]
        parsedend = parsedstart[1].split(']')
        parsedlist = parsedend[0].split(',')
        table.put_item(
            Item= {  
                'pk': 'AWS#',
                'sk': 'SERVICE#'+theshortname,
                'name': thelongname,
                'service': theshortname,
                'expire': int(new.timestamp()),
                'lastseen': str(orig)
            }
        )      
        for action in parsedlist:
            theaction = action[1:-1]
            table.put_item(
                Item= {
                    'pk': 'AWS#',
                    'sk': 'ACTION#'+theshortname+'#'+theaction,
                    'bk': 'ACTION#'+theaction+'#'+theshortname,
                    'name': thelongname,
                    'service': theshortname,
                    'action': theaction,
                    'expire': int(new.timestamp()),
                    'lastseen': str(orig)
                }
            ) 

    return {
        'statusCode': 200,
        'body': json.dumps('aws-policy-service-action')
    }
    