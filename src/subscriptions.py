import stripe
import os
import logging

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
    if data['type'] == 'checkout.session.async_payment_succeeded':
      session = data['data']['object']
      return session
    elif data['type'] == 'checkout.session.completed':
      session = data['data']['object']
      return session
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