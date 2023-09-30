import boto3
from openAI import *
from random import randint
import datetime

def create_listing(user, prompt):
    print('##############Generating Listing on OpenAI######################')
    listing = generate_ai_listing(prompt)
    print(listing)

    dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")
    print('##############Fetching User Details######################')

    sub = get_user(user,dynamodb_client=dynamodb_client)
    isSubscribed = sub['subscriptionType'] in ['Basic'] and sub['listingsRemaining'] > 0    

    print('##############Creating new Checkout object in Dynamo######################')
    res= create_checkout(user, listing, isSubscribed, dynamodb_client=dynamodb_client)

    if isSubscribed:
        print('##############Updating Remaining monthly Calls######################')

        decrement_subscription(user, dynamodb_client=dynamodb_client)
        
    res['checkoutID'] = int(res['checkoutID'])


    return res

def create_checkout(user, listing, isSubscribed,dynamodb_client=None):
    if dynamodb_client is None:
        dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")

    table = dynamodb_client.Table('assissted-listing-checkout')

    id = createUniqueCheckoutID(dynamodb_client=dynamodb_client)
    createTS = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S:%f')
    paid=True if isSubscribed else False
    paidTS= createTS if isSubscribed else None

    response = table.put_item(
        Item={
            'checkoutID':id,
            'createTS':createTS,
            'paidTS':paidTS,
            'userID':user,
            'paid':paid,
            'listing':listing,
              } 
    )

    print(response)
    return table.get_item(Key={
            'checkoutID': id
        })['Item']

    

def createUniqueCheckoutID(dynamodb_client=None):
    print('#############Generate Unique CheckoutID###############')
    if dynamodb_client is None:
        dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")
    
    table = dynamodb_client.Table('assissted-listing-checkout')

    checkoutID = -1
    generating=True
    
    while generating:
        checkoutID = randint(1000000, 10000000)
        try:
            res = table.get_item(Key={
            'checkoutID': checkoutID
        })
            print(res)
            a = res['Item']
            
        except:
            print(checkoutID)
            return checkoutID
    





def get_checkout(id, dynamodb_client=None):
    if dynamodb_client is None:
        dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")

    table = dynamodb_client.Table('assissted-listing-checkout')
    response = table.get_item(
        Key={
            'checkoutID': int(id)
        }
    )

    
    try:
        response['Item']['checkoutID'] = int(response['Item']['checkoutID'])
        return response['Item']
    except:
        #TODO Error handling
        return {'checkoutID': int(id)}
    
def purchase_checkout(checkoutID, dynamodb_client=None):
    print(checkoutID)
    if dynamodb_client is None:
        dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")

    table = dynamodb_client.Table('assissted-listing-checkout')
    response = table.update_item(
        Key={
            'checkoutID': int(checkoutID)
        },
        UpdateExpression='''SET 
    paid = :paid,
    paidTS = :paidTS
    
    ''',
        ExpressionAttributeValues={
            ':paid': True,
            ':paidTS': datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S:%f')
              }
    )

    return response




def subscription_created(email, subscriptionID, customerID, planType, listingPerMonth):

    dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")

    table = dynamodb_client.Table('assisted-listing-user')
    response = table.update_item(
        Key={
            'email': email
        },
        UpdateExpression='''SET 
    subscribedFlag = :subscribed,
    stripeCustID = :stripeCustID,
    subscriptionID = :subscriptionID,
    subscriptionType = :planType,
    listingsRemaining = :listingRemaining
    
    ''',
        ExpressionAttributeValues={
            ':subscribed': True,
            ':stripeCustID':customerID,
            ':subscriptionID': subscriptionID,
            ':planType':planType,
            ':listingRemaining': listingPerMonth  }
    )
    print(response)
    return response



def get_user(email,dynamodb_client=None):
    if dynamodb_client is None:
        dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")

    table = dynamodb_client.Table('assisted-listing-user')
    response = table.get_item(Key={
            'email': email
        })
    
    print(response)
    return(response['Item'])

def decrement_subscription(email, dynamodb_client=None):
    if dynamodb_client is None:
        dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")

    table = dynamodb_client.Table('assisted-listing-user')
    response = table.update_item(
        Key={
            'email': email
        },
        UpdateExpression='''SET 
    listingsRemaining = listingsRemaining + :val
    
    ''',
     ExpressionAttributeValues={
        ':val': -1
    },
    )
    print(response)
    return response

def create_user(email, userID):
    dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")

    table = dynamodb_client.Table('assisted-listing-user')

    res = table.put_item(Item={
            'email':email,
            'userID':userID,
            'stripeCustID':None,
            'subscribedFlag':False,
            'subscriptionID':None,
            'subscriptionType':None,
            'listingsRemaining':0
              } 
              )
    
    return res

def purchase_listing_with_subscription(checkoutID):
    dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")

    print('################Purchasing Listing with subscription######################')
    checkout = get_checkout(checkoutID, dynamodb_client)
    email = checkout['userID']
    print(f'###########Retrieved checkout {checkoutID} by {email}################')


    user = get_user(email, dynamodb_client)
    print(f'###########Retrieved User {email}################')


    if int(user['listingsRemaining']) > 0:
        purchase_checkout(checkoutID)
        print('Checkout is purchased')
        decrement_subscription(email, dynamodb_client)
        print('Decrement remaining subscriptions')
        return user
    else:
        #TODO error handling
        print('User does not have any listing remaining for this month')
        return user


purchase_listing_with_subscription(1194073)



#subscription_created('mikea0009@gmail.com', 'sub_1NpP8lAtI9Pqdjf0GcNKSrYV', 'cus_OceR8SWpK9lnY7', 'Basic', 12)
#prompt = '''Write me a real estate description about a 2200sqft, Condo located in Manchester, #Connecticut. This home with Solar heating and featuring Basketball Court, and Solar Panel.It #has 2.2 acres of land '''
#print(create_listing('mikea0009@gmail.com', prompt))



