# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

# Run doctests like this::
#     $ python -m doctest splash.py

import calendar
import collections
import copy
import csv
import datetime
import logging
import os

log = logging.getLogger("splash")


def check_is_last_day_of_month(dt):

    """
    >>> check_is_last_day_of_month(datetime.date(2017, 2, 27))
    False

    >>> check_is_last_day_of_month(datetime.date(2017, 2, 28))
    True
    """

    return calendar.monthrange(dt.year, dt.month)[1] == dt.day


class StartingData(object):

    def __init__(self):
        self.user_ids = set([])
        self.d = dict()

    def load_csv(self):

        for row in csv.DictReader(
            open(os.path.join("datafiles", "StartingData.csv"))):

            self.d[row["User Id"]] = dict(
                program=row["Program"],
                initial_amount=int(row["Initial Amount"]))

            self.user_ids.add(row["User Id"])

    @property
    def program_one_user_ids(self):

        for user_id in sorted(self.user_ids, key=int):

            v = self.d[user_id]

            if v["program"] == '1':
                yield user_id

    @property
    def program_two_user_ids(self):

        for user_id, v in self.d.items():
            if v["program"] == '2':
                yield user_id


class Transactions(object):

    def __init__(self):
        self.d = dict()

    def load_csv_files(self, known_user_ids):

        for filename in ["Jan.csv", "Feb.csv", "Mar.csv"]:

            for row in csv.DictReader(
                open(os.path.join("datafiles", filename))):

                if row["User Id"] not in known_user_ids:
                    raise KeyError(
                        "Could not find initial amount for {User Id}!".format(**row))
                else:

                    dt = datetime.datetime.strptime(row["Date"], "%Y-%m-%d").date()
                    self.d[(dt, row["User Id"])] = int(row["Amount"])

class RunningBalanceBuilder(object):

    def __init__(self, starting_balances, transactions):
        self.d = dict()
        self.starting_balances = starting_balances
        self.transactions = transactions
        self.last_days_of_months = set([])

    def write_rb_csv(self):

        rb_csv = csv.DictWriter(
            open(os.path.join("reports", "py-running-balances.csv"), "w"),
            [
                'dt',
                'user_id',
                'initial_amount',
                'program',
                'deposit',
                'total_deposits',
                'total_deposits_for_month',
                'current_balance',
                'total_transaction_count',
                'total_transaction_count_for_month',
                'is_last_day_of_month'])

        rb_csv.writeheader()

        for user_id in sorted(self.starting_balances.user_ids, key=int):

            total_deposits = 0
            total_deposits_for_month = 0
            total_transaction_count = 0
            total_transaction_count_for_month = 0
            current_balance = self.starting_balances.d[user_id]["initial_amount"]

            for dt in self.dates:

                is_first_day_of_month = dt.day == 1

                if is_first_day_of_month:
                    total_deposits_for_month = 0
                    total_transaction_count_for_month = 0

                is_last_day_of_month = check_is_last_day_of_month(dt)

                if is_last_day_of_month:
                    self.last_days_of_months.add(dt)

                k = (dt, user_id)

                deposit = self.transactions.d.get(k, 0)
                total_deposits += deposit
                total_deposits_for_month += deposit

                # In other words, if this user made a deposit on this date
                if k in self.transactions.d:
                    total_transaction_count += 1
                    total_transaction_count_for_month += 1
                    current_balance += deposit

                row = dict(
                    user_id=user_id,
                    dt=dt,
                    initial_amount=self.starting_balances.d[user_id]["initial_amount"],
                    program=self.starting_balances.d[user_id]["program"],
                    deposit=deposit,
                    total_deposits=total_deposits,
                    total_deposits_for_month=total_deposits_for_month,
                    total_transaction_count=total_transaction_count,
                    total_transaction_count_for_month=total_transaction_count_for_month,
                    is_last_day_of_month=is_last_day_of_month,
                    current_balance=current_balance)

                rb_csv.writerow(row)

                self.d[k] = row

        log.info("Finished writing py-running-balances.csv")

        return self

    @property
    def dates(self):

        for dt in self.daterange_generator(
            datetime.date(2017, 01, 01),
            datetime.timedelta(days=1),
            datetime.date(2017, 04, 1)):

            yield dt


    @staticmethod
    def daterange_generator(from_this_date, increment, until_this_date):

        """
        Yield datetimes from_this_date + increment until until_this_date.

        >>> a = datetime.datetime.now()

        >>> b = a + datetime.timedelta(minutes=1)

        >>> len(list(RunningBalanceBuilder.daterange_generator(a, datetime.timedelta(minutes=1), b)))
        1

        >>> list(RunningBalanceBuilder.daterange_generator(b, datetime.timedelta(minutes=1), a))
        []
        """

        x = copy.copy(from_this_date)

        while x < until_this_date:
            yield x
            x += increment

    def find_users_with_penalties(self):

        if not self.d:
            raise ValueError("Sorry, you need to write the CSV first!")

        else:

            for user_id in self.starting_balances.program_one_user_ids:

                minimum_monthly_deposit = 300
                minimum_monthly_transactions = 5
                minimum_end_of_month_balance = 1200

                for dt in sorted(self.last_days_of_months):

                    row = self.d[(dt, user_id)]

                    if row["total_deposits_for_month"] < minimum_monthly_deposit \
                    and row["total_transaction_count_for_month"] < minimum_monthly_transactions \
                    and row["current_balance"] < minimum_end_of_month_balance:

                        yield row

            for user_id in self.starting_balances.program_two_user_ids:

                minimum_monthly_deposit = 800
                minimum_monthly_transactions = 1
                minimum_end_of_month_balance = 5000

                for dt in sorted(self.last_days_of_months):

                    row = self.d[(dt, user_id)]

                    if row["total_deposits_for_month"] < minimum_monthly_deposit \
                    and row["total_transaction_count_for_month"] < minimum_monthly_transactions \
                    and row["current_balance"] < minimum_end_of_month_balance:

                        yield row

    def write_user_penalty_report(self):

        user_penalties = collections.defaultdict(int)

        for row in self.find_users_with_penalties():

            if row["program"] == "1":
                user_penalties[row["user_id"]] += 8

            elif row["program"] == "2":
                user_penalties[row["user_id"]] += 4

            else:
                raise ValueError("Unknown program! {program!r}".format(**row))

        penalty_csv = csv.DictWriter(
            open(os.path.join("reports", "py-users-with-penalties.csv"), "w"),
            [
                "user_id",
                "program",
                "total_penalties"
            ])

        penalty_csv.writeheader()

        for user_id in sorted(user_penalties, key=int):

            total_penalties = user_penalties[user_id]
            program = self.starting_balances.d[user_id]["program"]

            penalty_csv.writerow(dict(
                user_id=user_id,
                total_penalties=total_penalties,
                program=program))

        log.info("Finished writing py-users-with-penalties.csv")

    @staticmethod
    def log_row(row):

        log.debug(
            "{dt} user {user_id} (program {program}): "
            "monthly deposits: {total_deposits_for_month}, "
            "total transactions: {total_transaction_count_for_month}, "
            "current balance: {current_balance}".format(**row))

    def show_user_eom_values(self, user_id):

        for dt in sorted(self.last_days_of_months):
            row = self.d[(dt, str(user_id))]
            self.log_row(row)

    def find_highest_monthly_deposits(self):

        for dt in sorted(self.last_days_of_months):

            high_score = 0
            high_scoring_user_ids = set([])

            for user_id in sorted(self.starting_balances.user_ids, key=int):

                row = self.d[(dt, user_id)]

                if row["total_deposits_for_month"] > high_score:
                    high_score = row["total_deposits_for_month"]
                    high_scoring_user_ids = set([row["user_id"]])

                elif row["total_deposits_for_month"] == high_score:
                    high_scoring_user_ids.add(row["user_id"])

            yield (dt, high_score, high_scoring_user_ids)

    def write_highest_monthly_deposits_csv(self):

        highest_deposits_csv = csv.DictWriter(
            open(
                os.path.join(
                    "reports",
                    "py-highest-monthly-deposits.csv"),
                "w"),
            [
                "dt",
                "user_id",
                "total_deposits_for_month"
            ])

        highest_deposits_csv.writeheader()

        for dt, high_score, high_scoring_user_ids in self.find_highest_monthly_deposits():

            for user_id in high_scoring_user_ids:

                highest_deposits_csv.writerow(dict(
                    dt=dt,
                    user_id=user_id,
                    total_deposits_for_month=high_score))


        log.info("Wrote py-highest-monthly-deposits.csv")

    def find_most_monthly_transactions(self):

        for dt in sorted(self.last_days_of_months):

            high_score = 0
            high_scoring_user_ids = set([])

            for user_id in sorted(self.starting_balances.user_ids, key=int):

                row = self.d[(dt, user_id)]

                if row["total_transaction_count_for_month"] > high_score:
                    high_score = row["total_transaction_count_for_month"]
                    high_scoring_user_ids = set([row["user_id"]])

                elif row["total_transaction_count_for_month"] == high_score:
                    high_scoring_user_ids.add(row["user_id"])

            yield (dt, high_score, high_scoring_user_ids)

    def write_most_monthly_transactions_csv(self):

        most_monthly_transactions_csv = csv.DictWriter(
            open(
                os.path.join(
                    "reports",
                    "py-most-monthly-transactions.csv"),
                "w"),
            [
                "dt",
                "user_id",
                "total_transaction_count_for_month"
            ])

        most_monthly_transactions_csv.writeheader()

        for dt, high_score, high_scoring_user_ids in self.find_most_monthly_transactions():

            for user_id in high_scoring_user_ids:

                most_monthly_transactions_csv.writerow(dict(
                    dt=dt,
                    user_id=user_id,
                    total_transaction_count_for_month=high_score))

        log.info("Wrote py-most-monthly-transactions.csv")


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    starting_data = StartingData()
    starting_data.load_csv()

    transactions = Transactions()
    transactions.load_csv_files(starting_data.user_ids)

    rbb = RunningBalanceBuilder(starting_data, transactions)
    rbb.write_rb_csv()

    rbb.write_user_penalty_report()
    rbb.write_highest_monthly_deposits_csv()
    rbb.write_most_monthly_transactions_csv()

    log.info("All done!")
