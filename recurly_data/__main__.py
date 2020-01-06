# pylint: disable=missing-module-docstring,invalid-name
import argparse
import os
from recurly_data.recurly_data import RecurlyData
from colorama import Fore
from recurly_data.config import (
    RECURLY_API, RECURLY_KEY, STRIPE_KEY, STRIPE_API, SENTRY
)
from . import __version__


description = (
    "Recurly Data Generator, generates customer data onto a csv file. Please "
    "use a .env file to set RECURLY_KEY and STRIPE_KEY, or simply export the "
    "environment variables before running this script. You can also set these "
    "keys using --recurly-key and --stripe-key flags."
)
prog = f"recurly_data {__version__}"
parser = argparse.ArgumentParser(
    description=description,
    prog=prog,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
group = parser.add_mutually_exclusive_group()
group.add_argument(
    "-q",
    "--quiet",
    default=False,
    action="store_true",
    help="Silent output."
)
group.add_argument(
    "-v",
    "--verbose",
    default=False,
    action="count",
    help="Increase output verbosity.",
)

parser.add_argument(
    "--version",
    action='version',
    version=__version__,
    help="Get the package version."
)

parser.add_argument(
    "-l",
    "--limit",
    type=int,
    help="Set a limit for the number of records."
)

parser.add_argument(
    "-f",
    "--file",
    type=str,
    default="recurly_data.csv",
    help=(
        "The filename where records should be stored. "
        "A file will be created if it doesn't already exist."
    )
)

parser.add_argument(
    "--begin-time",
    type=str,
    help=(
        "Filters records to only include those with datetimes greater than or "
        "equal to the supplied datetime. Accepts an ISO 8601 date or date and "
        "time."
    )
)

parser.add_argument(
    "--end-time",
    type=str,
    help=(
        "Filters records to only include those with datetimes less than or "
        "equal to the supplied datetime. Accepts an ISO 8601 date or date and "
        "time."
    )
)

parser.add_argument(
    "--order",
    type=str,
    default="asc",
    choices=["asc", "desc"],
    help=(
        "The order in which products will be returned: asc for ascending "
        "order, desc for descending order."
    )
)

parser.add_argument(
    "--subscription-state",
    type=str,
    default="live",
    choices=[
        "active", "paused", "canceled", "expired",
        "future", "in_trial", "live", "past_due"
    ],
    help="The state of subscriptions to return."
)

parser.add_argument(
    "--recurly-key",
    type=str,
    default=RECURLY_KEY,
    help=(
        "The Recurly API Key. "
        "This option overrides the environment variable 'RECURLY_KEY'."
    )
)

parser.add_argument(
    "--stripe-key",
    type=str,
    default=STRIPE_KEY,
    help=(
        "The Stripe API Key. "
        "This option overrides the environment variable 'STRIPE_KEY'."
    )
)

parser.add_argument(
    "--recurly-api",
    type=str,
    default=RECURLY_API,
    help=(
        "The Recurly API base url. "
        "This option overrides the environment variable 'RECURLY_API'."
    )
)

parser.add_argument(
    "--stripe-api",
    type=str,
    default=STRIPE_API,
    help=(
        "The Stripe API base url. "
        "This option overrides the environment variable 'STRIPE_API'."
    )
)

parser.add_argument(
    "--sentry",
    type=str,
    default=SENTRY,
    help=(
        "Supply the custom sentry url. "
        "Connect with your team/personal sentry account. "
        "This option overrides the environment variable 'SENTRY'."
    )
)

args = parser.parse_args()

if args.recurly_key:
    rcd = RecurlyData(
        limit=args.limit,
        silence=args.quiet,
        verbose=args.verbose,
        filename=args.file,
        begin_time=args.begin_time,
        end_time=args.end_time,
        order=args.order,
        subscription_state=args.subscription_state,
        api=args.recurly_api,
        api_key=args.recurly_key,
        stripe_api=args.stripe_api,
        stripe_key=args.stripe_key,
    )









    # print(rcd.get_first_account_datetime())
    # print(rcd.get_accounts())
    # print(rcd.total_accounts)
    # print(rcd.api_limit)
    # print(rcd.api_limit_remaining)
    # print(rcd.api_limit_reset_time)
    #rcd.extract_data()
    rcd.make_csv()
else:
    print(Fore.RED + "Missing reculry api key.")
