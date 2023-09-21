import boto3


def get_checkout(id):
    dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")

    table = dynamodb_client.Table('assisted-listing-checkouts')
    response = table.get_item(
        Key={
            'checkoutID': id
        }
    )
    return response['Item']


def create_checkout(user):
    pass


def get_user(email):
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


subscription_created('mikea0009@gmail.com', 'sub_1NpP8lAtI9Pqdjf0GcNKSrYV', 'cus_OceR8SWpK9lnY7', 'Basic', 12)
