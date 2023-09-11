import boto3

def get_checkout(id):
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")


    response = dynamodb_client.get_item(
    TableName='assisted-listing-checkouts',
    Key={
        'checkoutID': {'S': id}
    }
)
    return response['Item']

def create_checkout(user):
    pass