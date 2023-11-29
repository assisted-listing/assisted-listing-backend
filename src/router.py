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
    
    
    try:
        logging.error(event['triggerSource'])

        if event['triggerSource']== 'PostConfirmation_ConfirmSignUp':
            email = event['request']['userAttributes']['email']
            sub = event['request']['userAttributes']['sub']
            result = create_user(email, sub)
            logging.info('RESULT:')
            logging.info(result)
            return { 
                'statusCode': 200,
                'body': json.dumps(result)
            }
    except Exception as error:
        logging.error('error: ')
        logging.error(error)
            
    

    try:
        method = event['httpMethod']
        if method == 'OPTIONS':
            return { 
            'statusCode': 200,
            'body': json.dumps("Successful preflight")
        }
    except:
        pass
    
    try:
        body = json.loads(event['body'])
        logging.info('Body:')

        logging.info(body)
        logging.info('&'*100)
    except:
        body = {}
        
     
    path = event['path'][1:]    
    statusCode = 200
    if path == 'checkout':
        
        if method == 'POST':
            result = create_listing(body['body']['user'], body['body']['prompt'])
        elif method == 'GET': #GET
            params = event['queryStringParameters']
            result = get_checkout(params['checkoutID'])
        else:
            params = event['queryStringParameters']
            result = purchase_listing_with_subscription(body['body']['email'], body['body']['checkoutID'])
            
    elif path == 'subscription_change':
        result = handle_subscription(body, event)
    elif path == 'user':
        if method == 'POST':
            result = create_user(body['email'], body['subID'])
        if method == 'GET':
            params = event['queryStringParameters']
            result = get_user(params['userID'])
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
