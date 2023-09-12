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

get_checkout('12345678')