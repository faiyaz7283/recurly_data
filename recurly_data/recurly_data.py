"""Recurly Data."""
# pylint: disable=import-error,wildcard-import,unused-wildcard-import
import csv
from datetime import datetime, timezone
import os
from typing import Dict, List, Optional, Union
import json
import recurly
import requests
from colorama import init, Fore, Back, Style
from tqdm import tqdm
import sentry_sdk
from recurly_data.config import (
    RECURLY_API, RECURLY_KEY, STRIPE_KEY, STRIPE_API, SENTRY
)
import pickle
#from recurly_data.logger import Logger
init(autoreset=True)

if SENTRY:
    sentry_sdk.init(SENTRY)


# pylint: disable=too-many-instance-attributes
class RecurlyData:
    """
    Recurly data.
    """

    def __header_response(self):
        """Get information from headers."""
        status = False

        if self.api_key:
            response = requests.head(
                self.api + "/accounts",
                auth=(self.api_key, "")
            )

            if response.status_code == 200:
                status = True
                self.api_total_accounts = int(response.headers["X-Records"])
                self.api_limit = int(response.headers["X-RateLimit-Limit"])
                self.api_limit_remaining = int(
                    response.headers["X-RateLimit-Remaining"]
                )
                self.api_limit_reset_time = (
                    datetime.fromtimestamp(
                        int(response.headers["X-RateLimit-Reset"])
                    )
                )

        return status

    # pylint: disable=too-many-arguments
    def __init__(
            self,
            limit: int = None,
            silence: Union[int, bool] = False,
            verbose: Union[int, bool] = False,
            filename: str = "recurly_data.csv",
            begin_time: Optional[str] = None,
            end_time: Optional[str] = None,
            order: str = "asc",
            subscription_state: str = "live",
            api: Optional[str] = RECURLY_API,
            api_key: Optional[str] = RECURLY_KEY,
            stripe_key: Optional[str] = STRIPE_KEY,
            stripe_api: Optional[str] = STRIPE_API,
            total_remaining: Optional[int] = None,
    ):
        # Set the keys and values
        self.limit = limit
        self.silence = silence
        self.verbose = int(verbose)
        self.filename = os.path.abspath(
            os.path.expanduser(
                os.path.expandvars(
                    filename
                )
            )
        )
        self.__pickle = "script_info.pickle"
        self.begin_time = begin_time
        self.end_time = end_time
        self.order = order
        self.subscription_state = subscription_state
        self.api = api
        self.api_key = api_key
        self.stripe_key = stripe_key
        self.stripe_api = stripe_api
        self.total_remaining = total_remaining
        self.client = recurly.Client(self.api_key)
        self.recurly_data: List[Dict[str, Union[str, int]]] = []
        self.api_total_accounts = 0
        self.api_limit_reset_time: Union[int, float, datetime] = 0
        self.api_limit: int = 0
        self.api_limit_remaining: int = 0
        self.call_recurly_api("headers")
        self.progress_bar: tqdm = self.__progress_bar()

    def __progress_bar(self):
        ncols = 100
        total = None
        if self.total_remaining:
            total = self.total_remaining
        elif self.limit:
            total = self.limit
        elif not self.begin_time and not self.end_time:
            total = self.api_total_accounts

        pnct_bar = "{percentage:3.0f}% " + Fore.GREEN + "{bar}" + Fore.RESET
        extr = "Extracted: " + Fore.YELLOW + "{n_fmt}/{total_fmt}" + Fore.RESET
        elps = "Elapsed: " + Fore.YELLOW + "{elapsed}<{remaining}" + Fore.RESET
        rate = "Rate: " + Fore.YELLOW + "{rate_fmt}" + Fore.RESET

        if not self.verbose:
            bar_format = pnct_bar + "|"
        else:
            bar_format = f"{pnct_bar} | {extr} | {elps} | {rate}"

        return tqdm(
            total=total,
            ncols=ncols,
            bar_format=bar_format,
            disable=self.silence,
        )

    def call_recurly_api(self, endpoint: str, **params):
        """A convenient way to call recurly api with an endpoint."""
        allowed_endpoints = [
            "headers", "accounts", "subscriptions", "redemptions"
        ]

        if endpoint not in allowed_endpoints:
            msg = f"Allowed endpoints are {', '.join(allowed_endpoints)}."
            raise Exception(msg)

        try:
            if endpoint == "headers":
                response = self.__header_response()
            elif endpoint == "accounts":
                # refresh counts
                self.__header_response()
                response = self.client.list_accounts(**params, subscriber="true").items()
            elif endpoint == "subscriptions":
                response = self.client.list_account_subscriptions(
                    **params
                ).items()
            elif endpoint == "redemptions":
                response = self.client.list_account_coupon_redemptions(
                    **params
                ).items()
        except recurly.errors.ValidationError as excpt:
            print("here")
            print(f"ValidationError: {excpt.error.message}")
            print(excpt.error.params)
        except recurly.errors.NotFoundError as excpt:
            print(f"NotFoundError: {excpt}")
        except recurly.errors.ApiError as excpt:
            print(f"ApiError: {excpt}")
        except recurly.NetworkError as excpt:
            print(f"NetworkError: {excpt}")
        else:
            return response

    @staticmethod
    def compact_pending_change(obj):
        """Dictionary of compact pending change info."""
        return {
            "subject": obj.object,
            "new_plan_code": obj.plan.code,
            "new_plan_frequency": RecurlyData.get_frequency_name(obj.plan.name),
            "new_plan_pricing_amount": int(obj.unit_amount * 100),
            "new_plan_activate_at": str(obj.activate_at),
            "new_plan_activated": obj.activated
        }

    # pylint: disable=too-many-locals,too-many-branches
    def extract_data(self, **params):
        """Extract customer data."""

        idx, columns = 0, [
            "row", "email", "name", "stripe_id", "created_at", "frequency",
            "pricing_amount", "discounted_pricing_amount", "next_billing_date",
            "cancel_date", "active_promo_code", "pending_change"
        ]

        with self.progress_bar as pbar:
            for account in self.get_accounts(**params):
                row = {column: "" for column in columns}

                # if (
                #     self.last_row and
                #     self.last_row["email"] == account.email
                # ):
                #     continue

                account_id = account.id
                row["email"] = account.email
                if account.first_name:
                    row["name"] = account.first_name
                if account.last_name:
                    row["name"] = f"{row['name']} {account.last_name}"
                row["stripe_id"] = self.get_assoc_stripe_id(account.email)
                row["created_at"] = str(account.created_at)

                for subscription in self.get_account_subscriptions(account_id):
                    row["frequency"] = self.get_frequency_name(subscription.plan.name)
                    row["pricing_amount"] = int(subscription.unit_amount * 100)
                    nbd = subscription.current_term_ends_at
                    if nbd:
                        row["next_billing_date"] = str(nbd)

                    cncd = subscription.canceled_at
                    if cncd:
                        row["cancel_date"] = str(cncd)
                    pending_change = subscription.pending_change
                    if pending_change:
                        row["pending_change"] = (
                            self.compact_pending_change(pending_change)
                        )

                for redemption in self.get_account_redemptions(account_id):
                    if redemption.state == "active":
                        coupon = redemption.coupon
                        code = coupon.code
                        row["active_promo_code"] = code
                        if row["pricing_amount"]:
                            price = self.get_discounted_price(int(row["pricing_amount"]), coupon.discount)
                            row["discounted_pricing_amount"] = price

                self.recurly_data.append(row)
                idx += 1
                row["row"] = idx
                item_count = 0
                for key, item in row.items():
                    item_count += 1
                    if key == "pending_change":
                        item = "yes" if item else ""
                    pbar.display(msg=f" {key}: {Fore.CYAN}{item}", pos=item_count)
                    pbar.refresh()
                pbar.update()
                if self.limit and idx == self.limit:
                    break

    def get_account_redemptions(self, account_id: str, **params):
        """Get recurly account's redemptions iterator object."""
        params["account_id"] = account_id
        params["endpoint"] = "redemptions"
        return self.call_recurly_api(**params)

    def get_account_subscriptions(self, account_id: str, **params):
        """Get recurly account's subscriptions iterator object."""
        params["account_id"] = account_id
        params["endpoint"] = "subscriptions"
        if "state" not in params:
            params["state"] = self.subscription_state

        return self.call_recurly_api(**params)

    def get_accounts(self, **params):
        """Get recurly accounts iterator object."""
        params["endpoint"] = "accounts"

        if "order" not in params:
            params["order"] = self.order

        if "begin_time" not in params and self.begin_time:
            params["begin_time"] = self.begin_time

        if "end_time" not in params and self.end_time:
            params["end_time"] = self.end_time

        return self.call_recurly_api(**params)

    def get_assoc_stripe_id(self, email: str) -> Optional[str]:
        """
        Get the asscociated stripe id.
        """
        cst_id = ""
        if self.stripe_api:
            item = requests.get(
                self.stripe_api + "/customers",
                auth=(self.stripe_key, ""),
                params={"email": email}
            )

            if item.status_code == 200:
                data = item.json()["data"]
                if data:
                    cst_id = data[0]["id"]

        return cst_id

    @staticmethod
    def get_discounted_price(price: int, discount):
        discount_type = discount.type
        if discount_type == "percent":
            price = int(
                price - (price * discount.percent/100)
            )
        elif discount_type == "fixed":
            price = int(
                price - (discount.currencies[0].amount * 100)
            )
        return price

    def get_first_account_datetime(self):
        """Get datetime of the first record."""
        accounts = self.get_accounts(order="asc")
        # TODO: Catch exception recurly.ApiError, AttributeError etc
        account = next(accounts)
        return account.created_at

    @staticmethod
    def get_frequency_name(name: str):
        """Get the frequency name."""
        name = name.split(' ')[0]
        if(name == "Annual"):
            name = "Yearly"
        return name

    def make_csv(self):
        """Make  a csv file from extracted data."""
        try:
            self.extract_data()
        except KeyboardInterrupt as excpt:
            print(str(excpt))
        finally:
            last_row = False
            if self.recurly_data:
                total_rows = len(self.recurly_data) - 1
                last_row = self.recurly_data[total_rows]
                mode = "a" if os.path.exists(self.filename) else "w"
                fieldnames = list(self.recurly_data[0].keys())
                with open(self.filename, mode=mode) as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    if mode == "w":
                        writer.writeheader()
                    for row in self.recurly_data:
                        writer.writerow(row)
