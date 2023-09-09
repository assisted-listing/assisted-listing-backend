import stripe
import os

stripe.api_key = os.environ['stripe_key_test']
endpoint_secret = os.environ['webhook_secret']



def handle_subscription(data, headers):
    event = None
    payload = data
    sig_header = headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'checkout.session.async_payment_succeeded':
      session = event['data']['object']
      return session
    elif event['type'] == 'checkout.session.completed':
      session = event['data']['object']
      return session
    elif event['type'] == 'subscription_schedule.aborted':
      subscription_schedule = event['data']['object']
      return session
    elif event['type'] == 'subscription_schedule.canceled':
      subscription_schedule = event['data']['object']
      return session
    elif event['type'] == 'subscription_schedule.completed':
      subscription_schedule = event['data']['object']
      return session
    elif event['type'] == 'subscription_schedule.created':
      subscription_schedule = event['data']['object']
      return session
    elif event['type'] == 'subscription_schedule.expiring':
      subscription_schedule = event['data']['object']
      return session
    elif event['type'] == 'subscription_schedule.released':
      subscription_schedule = event['data']['object']
      return session
    elif event['type'] == 'subscription_schedule.updated':
      subscription_schedule = event['data']['object']
      return session
    else:
      print('Unhandled event type {}'.format(event['type']))