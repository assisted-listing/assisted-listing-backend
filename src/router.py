import json
import logging
from subscriptions import *
from database import *

def lambda_handler(event, context):
    #TODO set log level here from environment variable
    
    logging.info('*'*100)
    logging.error(event)
    logging.info('!'*100)
    logging.info(context)
    logging.info('@'*100)
    path = event['path'][1:]

    # try:
    #     user = event["queryStringParameters"]["user"]
    # except:
    #     statusCode = 503
    #     logging.error('must include user in API request like /user?testUser0')

    #     result = f'must include user in API request like /user?testUser0'
    #     return { 
    #     'statusCode': statusCode,
    #     'body': json.dumps(result)
    # }

    try:
        method = event['httpMethod']
        body = json.loads(event['body'])
        logging.info('Body:')

        logging.info(body)
        logging.info('&'*100)
    except:
        body = {}
        
    statusCode = 200
    if path == 'checkout':
        if method == 'GET':
            params = event['queryStringParameters']
            result = get_checkout(params['checkoutID'])
        if method == 'POST':
            result = create_checkout(body['user'])
            
    if path == 'subscription_change':
        result = handle_subscription(body, event)
    elif path == 'new_user':
        result = 'new_users'
    else:
        statusCode = 503
        logging.error('{path} is not a valid endpoint')
        result = f'{path} is not a valid endpoint'
    logging.info('RESULT:')
    logging.info(result)
    return { 
        'statusCode': statusCode,
        'body': json.dumps(result)
    }
