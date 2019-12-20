""" Vimeo Data. """
# pylint: disable=import-error,wildcard-import,unused-wildcard-import
import csv
from datetime import timezone
from typing import Dict, List, Optional, Union
import json
import recurly
import requests
from colorama import init, Fore, Back, Style
from tqdm import tqdm
from recurly_data.config import RECURLY_KEY, STRIPE_KEY, STRIPE_API, SENTRY
#from recurly_data.logger import Logger
#import sentry_sdk
init(autoreset=True)
#sentry_sdk.init(SENTRY)


# pylint: disable=too-many-instance-attributes
class RecurlyData:
    """
    Recurly data.
    """

    # pylint: disable=too-many-arguments
    def __init__(
            self,
            limit: int = None,
            silence: Union[int, bool] = False,
            verbose: Union[int, bool] = False,
            filename: str = "recurly_data.csv",
            api_key: Optional[str] = RECURLY_KEY,
            stripe_key: Optional[str] = STRIPE_KEY,
            stripe_api: Optional[str] = STRIPE_API,
    ):
        # Set the keys and values
        self.limit = limit
        self.silence = silence
        self.verbose = int(verbose)
        self.filename = filename
        self.api_key = api_key
        self.stripe_key = stripe_key
        self.stripe_api = stripe_api
        self.client = recurly.Client(self.api_key)
        self.recurly_data: List[Dict[str, Union[str, int]]] = []

    # pylint: disable=too-many-locals,too-many-branches
    def extract_data(self):
        """Extract customer data."""
        accounts = self.client.list_accounts()

        columns = ["email", "name", "stripe_id", "frequency", "pricing_amount",
                   "next_billing_date", "cancel_date", "active_promo_code",
                   "pending_change"]
        rows = []
        i = 0

        with tqdm(
                dynamic_ncols=True,
                bar_format=(
                    "Extracted: " + Fore.YELLOW + "{n_fmt}" + Fore.RESET + " | "
                    "Time elapsed: " + Fore.YELLOW + "{elapsed}" + Fore.RESET + " | "
                    "Rate: " + Fore.YELLOW + "{rate_fmt}"
                ),
                disable=self.silence
        ) as pbar:
            for account in accounts.items():
                row = {column: "" for column in columns}

                row["email"] = account.email
                if account.first_name:
                    row["name"] = account.first_name
                if account.last_name:
                    row["name"] = f"{row['name']} {account.last_name}"
                row["stripe_id"] = self.get_assoc_stripe_id(account.email)
                try:
                    subscriptions = self.client.list_account_subscriptions(
                        account.id, state="live"
                    )
                    for subscription in subscriptions.items():
                        row["frequency"] = subscription.plan.name.split(' ')[0]
                        row["pricing_amount"] = subscription.unit_amount
                        nbd = subscription.current_term_ends_at
                        if nbd:
                            nbd_timestamp = nbd.replace(
                                tzinfo=timezone.utc
                            ).timestamp()
                            row["next_billing_date"] = nbd_timestamp
                        cncd = subscription.canceled_at
                        if cncd:
                            cncd_timestamp = cncd.replace(
                                tzinfo=timezone.utc
                            ).timestamp()
                            row["cancel_date"] = cncd_timestamp
                        pending_change = subscription.pending_change
                        if pending_change:
                            row["pending_change"] = (
                                self.compact_pending_change(pending_change)
                            )
                except recurly.errors.NotFoundError as excpt:
                    pass
                    # Logger().error(str(excpt))

                try:
                    redemptions = self.client.list_account_coupon_redemptions(
                        account.id
                    )
                    for redemption in redemptions.items():
                        if redemption.state == "active":
                            row["active_promo_code"] = redemption.coupon.code
                except recurly.errors.NotFoundError as excpt:
                    pass
                    # Logger().error(str(excpt))

                if self.limit and i == self.limit:
                    break

                rows.append(row)
                i += 1

                if self.verbose:
                    msg = Fore.GREEN + row['email']
                    pbar.display(msg=msg, pos=1)

                pbar.update()
                # Logger().info(json.dumps(row))

        self.recurly_data = rows

    def make_csv(self):
        """Make  a csv file from extracted data."""
        if not self.recurly_data:
            self.extract_data()

        if self.recurly_data:
            with open('recurly_data.csv', mode='w') as csv_file:
                fieldnames = self.recurly_data[0].keys()
                writer = csv.DictWriter(csv_file, fieldnames)
                writer.writeheader()
                for row in self.recurly_data:
                    writer.writerow(row)

    @staticmethod
    def compact_pending_change(obj):
        """Dictionary of compact pending change info."""
        activate_at = obj.activate_at.replace(tzinfo=timezone.utc).timestamp()
        return {
            "subject": obj.object,
            "new_plan_code": obj.plan.code,
            "new_plan_frequency": obj.plan.name.split(' ')[0],
            "new_plan_pricing_amount": obj.unit_amount,
            "new_plan_activate_at": activate_at,
            "new_plan_activated": obj.activated
        }

    def get_assoc_stripe_id(self, email: str) -> Optional[str]:
        """
        Get the asscociated stripe id.
        """
        cst_id = ""
        if self.stripe_api:
            item = requests.get(
                self.stripe_api,
                auth=(self.stripe_key, ""),
                params={"email": email}
            )

            if item.status_code == 200:
                data = item.json()["data"]
                if data:
                    cst_id = data[0]["id"]

        return cst_id
