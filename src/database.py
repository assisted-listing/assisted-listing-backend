import boto3
from openAI import *
from random import randint
import datetime

x = '''
Welcome to this remarkable 2200sqft condo nestled in the vibrant town of Manchester, Connecticut. This one-of-a-kind residence offers an attractive blend of modern conveniences, eco-friendly features, and ample space to flourish. Situated on an extensive 2.2 acres of land, this truly is a sanctuary for those seeking a harmonious blend of comfort and sustainability.

As you step inside, you will be greeted by an inviting living area with an open concept layout, perfect for both relaxation and entertainment. The large windows bathe the space in natural light while offering panoramic views of the picturesque surroundings. The solar heating system ensures not only a warm and cozy ambiance throughout the year but also contributes to significant energy savings.

The kitchen in this condo is perfect for any culinary enthusiast, as it boasts top-of-the-line appliances, ample counter space, and elegant cabinetry. Whether you are hosting a dinner party or preparing a simple meal, this kitchen will exceed your every expectation.

This home also sets itself apart with unique and desirable amenities, including its very own basketball court where you can enjoy friendly competition with family and friends. Stay active and enjoy the outdoors in your own backyard sanctuary.

In addition to its sustainable features, this condo is equipped with solar panels, allowing you to harness the power of the sun and reduce your carbon footprint. Imagine the satisfaction of living in a home that not only provides comfort but also actively contributes to the preservation of the environment.

The thoughtful design of this condo continues with the spacious master suite, offering a private retreat at the end of the day. Complete with a luxurious en-suite bathroom and ample closet space, this room is a true haven of relaxation.

Two additional well-appointed bedrooms and a modern bathroom ensure that there is plenty of space for family and guests. With enough room to accommodate everyone's needs, this condo is ideal for both daily living and entertaining.

Conveniently situated in Manchester, this residence provides easy access to shopping centers, restaurants, and entertainment options. Enjoy the best of both worlds, with a peaceful escape from the hustle and bustle, yet just a short distance away from all the amenities you desire.

Welcome home to this remarkable 2200sqft condo, where sustainable living meets modern luxury. Embrace the abundance of space, energy-efficient features, basketball court, and solar panels all nestled on 2.2 acres of land, creating a haven you'll love to call your own.'''

def create_listing(user, prompt):
    print('##############Generating Listing on OpenAI######################')
    listing = generate_ai_listing(prompt)
    print(listing)

    dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")
    print('##############Fetching User Details######################')

    sub = get_subscription(user,dynamodb_client=dynamodb_client)
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

    response['Item']['checkoutID'] = int(response['Item']['checkoutID'])
    try:
        return response['Item']
    except:
        #TODO Error handling
        return {'checkoutID': int(id)}



def get_user(email, dynamodb_client=None):
    if dynamodb_client is None:
        dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")

    table = dynamodb_client.Table('assisted-listing-user')
    response = table.get_item(
        Key={
            'email': email
        }
    )
    print(response)
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



def get_subscription(email,dynamodb_client=None):
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





#subscription_created('mikea0009@gmail.com', 'sub_1NpP8lAtI9Pqdjf0GcNKSrYV', 'cus_OceR8SWpK9lnY7', 'Basic', 12)
#prompt = '''Write me a real estate description about a 2200sqft, Condo located in Manchester, #Connecticut. This home with Solar heating and featuring Basketball Court, and Solar Panel.It #has 2.2 acres of land '''
#print(create_listing('mikea0009@gmail.com', prompt))



