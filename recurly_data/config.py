import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

RECURLY_KEY = os.getenv("RECURLY_KEY")
RECURLY_API = os.getenv("RECURLY_API", "https://dropout.recurly.com/v2")
STRIPE_KEY = os.getenv("STRIPE_KEY")
STRIPE_API = os.getenv("STRIPE_API", "https://api.stripe.com/v1")
SENTRY = os.getenv("SENTRY")
PAPERTRAIL_DEST = os.getenv("PAPERTRAIL_DEST")
PAPERTRAIL_PORT = int(os.getenv("PAPERTRAIL_PORT")) if os.getenv("PAPERTRAIL_PORT") else None
