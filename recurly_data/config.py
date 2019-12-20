import os

RECURLY_KEY = os.getenv("RECURLY_KEY")
STRIPE_KEY = os.getenv("STRIPE_KEY")
STRIPE_API = os.getenv("STRIPE_API", "https://api.stripe.com/v1/customers")
SENTRY = os.getenv("SENTRY")
PAPERTRAIL_DEST = os.getenv("PAPERTRAIL_DEST")
PAPERTRAIL_PORT = int(os.getenv("PAPERTRAIL_PORT")) if os.getenv("PAPERTRAIL_PORT") else None
