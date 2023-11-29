import stripe
import os
import logging
import boto3
from database import *
from requests import *
from requests.auth import HTTPBasicAuth


logger = logging.getLogger()
logger.setLevel(logging.INFO)

stripe.api_key = os.environ['stripe_key_test']
endpoint_secret = os.environ['webhook_secret_test']


def handle_subscription(data, event):
    payload = data
    headers = event['headers']
    sig_header = headers['Stripe-Signature']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        logging.error(e)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logging.error(e)

    # Handle the event
    logging.info('*******TYPE OF HOOK*******')
    logging.info(data['type'])
    if data['type'] == 'checkout.session.async_payment_succeeded':
      session = data['data']['object']
      return session
    elif data['type'] == 'checkout.session.completed':
      session = data['data']['object']
      subscriptionID = session['subscription']
      email = session['customer_email']
      customer_creation = session['customer_creation']
      customerID = session['customer']
      payment_status = session['payment_status']
      planType, listingPerMonth = subscriptionPlanAttributes(subscriptionID)

      subscription_created(email, subscriptionID, customerID, planType, listingPerMonth)

      return f'Subscription created succesfully for {email}'
    elif data['type'] == 'subscription_schedule.aborted':
      subscription_schedule = data['data']['object']
      return subscription_schedule
    elif data['type'] == 'subscription_schedule.canceled':
      subscription_schedule = data['data']['object']
      return subscription_schedule
    elif data['type'] == 'subscription_schedule.completed':
      subscription_schedule = data['data']['object']
      return subscription_schedule
    elif data['type'] == 'subscription_schedule.created':
      subscription_schedule = data['data']['object']
      return subscription_schedule
    elif data['type'] == 'subscription_schedule.expiring':
      subscription_schedule = data['data']['object']
      return subscription_schedule
    elif data['type'] == 'subscription_schedule.released':
      subscription_schedule = data['data']['object']
      return subscription_schedule
    elif data['type'] == 'subscription_schedule.updated':
      subscription_schedule = data['data']['object']
      return subscription_schedule
    else:
      print('Unhandled event type {}'.format(data['type']))

def subscriptionPlanAttributes(sub_id = 'sub_1Nu7S2AtI9Pqdjf02K7b11Je'):
  res = get_subscripton_data(sub_id)
  logging.info(res)

  product = res['plan']['product']
  if 'prod_OaamIqqtpyycqc': 
     return 'Basic', 12
  else:
     return 'Basic', 12
  
def get_subscripton_data(sub_id = 'sub_1Nu7S2AtI9Pqdjf02K7b11Je'):
  auth = HTTPBasicAuth(os.environ['stripe_key_test'], '')
  res: requests.Response = requests.get(f'https://api.stripe.com/v1/subscriptions/{sub_id}', auth=auth)
  return res.json()

def update_purchase(user, subscription):
   pass
   

def new_subscription(email, customerID, subscriptionID):
   pass
   #find existing user in dynamo by email
   #update customerID if necessary (learn more about customerIDs)
   #set subscription flag to true
   #link subscriptionID
   #getSubscriptionType
   #set # of listing requests for the month

def cancel_subscription(sub_id):
   pass