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
        
        if method == 'POST':
            result = create_listing(body['user'], body['prompt'])
        else: #GET
            params = event['queryStringParameters']
            result = get_checkout(params['checkoutID'])
            
    elif path == 'subscription_change':
        result = handle_subscription(body, event)
    elif path == 'user':
        result = create_user(body['email'], body['subID'])
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
