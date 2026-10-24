import numpy as np
import pandas as pd
from faker import Faker

SEED = 42
COUNTRIES = ["LV", "DE", "GB", "FR"]
COUNTRY_WEIGHTS = [0.2, 0.3, 0.3, 0.2]
MERCHANT_CATEGORIES = ["gym", "saas", "utilities", "insurance", "media", "telecom"]
MAX_MANDATES = 3
END_DATE = pd.Timestamp("2026-10-15")
MANDATE_STATUS_WEIGHT = [0.9, 0.1]
MANDATE_STATUSES = ["active", "cancelled"]
PAYMENT_STATUS_WEIGHT = [0.08, 0.92]
PAYMENT_STATUSES = ["failed", "paid_out"]
PAYM_FAILURE_REASONS = [
    "insufficient_funds",
    "refer_to_payer",
    "account_closed",
    "mandate_cancelled",
]
PAYM_FAILURE_REASON_WEIGHT = [0.6, 0.2, 0.1, 0.1]


def generate_merchants(n: int, rng: np.random.Generator, fake: Faker) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "merchant_id": [f"MER{i:05d}" for i in range(1, n + 1)],
            "name": [fake.company() for _ in range(n)],
            "category": rng.choice(MERCHANT_CATEGORIES, size=n),
            "country": rng.choice(COUNTRIES, size=n, p=COUNTRY_WEIGHTS),
        }
    )


def generate_customers(n: int, rng: np.random.Generator, fake: Faker) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": [f"CUS{i:07d}" for i in range(1, n + 1)],
            "name": [fake.name() for _ in range(n)],
            "email": [fake.email() for _ in range(n)],
            "country": rng.choice(COUNTRIES, size=n, p=COUNTRY_WEIGHTS),
            "created_at": pd.Timestamp("2025-01-01")
            + pd.to_timedelta(rng.integers(0, 365, size=n), unit="D"),
        }
    )


def generate_mandates(
    customers: pd.DataFrame,
    merchants: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:

    n_per_customer = rng.integers(
        1, MAX_MANDATES + 1, size=len(customers)
    )  # 1, 2 or MAX_MANDATES mandates per customer
    m = customers.loc[customers.index.repeat(n_per_customer)].reset_index(drop=True)
    m = m.rename(columns={"created_at": "customer_created_at"})  # rename column

    m["merchant_id"] = rng.choice(merchants["merchant_id"], size=len(m))
    m = m.drop_duplicates(subset=["customer_id", "merchant_id"]).reset_index(drop=True)

    n = len(m)
    m["mandate_id"] = [f"MD{i:07d}" for i in range(1, n + 1)]

    is_gb = m["country"] == "GB"
    m["scheme"] = np.where(
        is_gb, "bacs", "sepa_core"
    )  # CASE WHEN country = 'GB' THEN 'bacs' ELSE 'sepa_core' END
    m["currency"] = np.where(is_gb, "GBP", "EUR")

    days_after = pd.to_timedelta(rng.integers(0, 180, size=n), unit="D")
    m["created_at"] = (m["customer_created_at"] + days_after).clip(upper=END_DATE)

    m["status"] = rng.choice(MANDATE_STATUSES, size=n, p=MANDATE_STATUS_WEIGHT)

    random_days = pd.to_timedelta(rng.integers(30, 300, size=n), unit="D")
    cancelled_date = m["created_at"] + random_days

    is_cancelled = (m["status"] == "cancelled") & (cancelled_date <= END_DATE)

    m["cancelled_at"] = cancelled_date.where(is_cancelled)
    m["status"] = np.where(is_cancelled, "cancelled", "active")

    return m[
        [
            "mandate_id",
            "customer_id",
            "merchant_id",
            "scheme",
            "currency",
            "status",
            "created_at",
            "cancelled_at",
        ]
    ]


# payment_id, mandate_id, amount, currency, charge_date, status, failure_reason, retry_of_payment_id
def generate_payments(
    mandates: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:

    m = mandates[mandates["status"] != "failed"].copy()  # only if you added "failed"
    n = len(m)
    m["charge_day"] = rng.integers(1, 29, size=n)  # 1-28: every month has these days
    m["amount"] = rng.choice([9.99, 19.99, 29.0, 49.5, 75.5, 120.0, 250.0], size=n)

    last_date = m["cancelled_at"].fillna(END_DATE)  # NVL(cancelled_at, :end_date)
    first_month = m["created_at"].dt.to_period("M")
    last_month = last_date.dt.to_period("M")
    m["n_payments"] = (last_month - first_month).apply(lambda x: x.n) + 1

    p = m.loc[m.index.repeat(m["n_payments"])].reset_index(drop=True)
    p["month_no"] = p.groupby("mandate_id").cumcount()  # 0, 1, 2, ... within each mandate

    p["charge_date"] = (
        p["created_at"].dt.to_period("M") + p["month_no"]
    ).dt.to_timestamp() + pd.to_timedelta(p["charge_day"] - 1, unit="D")

    last_date_of_that_row = p["cancelled_at"].fillna(END_DATE)
    p = p[
        (p["charge_date"] >= p["created_at"]) & (p["charge_date"] <= last_date_of_that_row)
    ].reset_index(drop=True)
    n_payments = len(p)

    p["payment_id"] = [f"PAY{i:07d}" for i in range(1, n_payments + 1)]

    p["status"] = rng.choice(PAYMENT_STATUSES, size=n_payments, p=PAYMENT_STATUS_WEIGHT)

    failure_reason = rng.choice(PAYM_FAILURE_REASONS, size=n_payments, p=PAYM_FAILURE_REASON_WEIGHT)
    status_failed = p["status"] == "failed"
    p["failure_reason"] = np.where(status_failed, failure_reason, None)

    return p[
        [
            "payment_id",
            "mandate_id",
            "amount",
            "currency",
            "charge_date",
            "status",
            "failure_reason",
        ]
    ]


# event_id,payment_id,status,event_at
def generate_events(payments: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    p = payments
    is_failed = p["status"] == "failed"

    def random_days(lo: int, hi: int, size: int) -> pd.Series:
        """A random number of days between lo and hi (inclusive) for each of `size` rows."""
        return pd.to_timedelta(rng.integers(lo, hi + 1, size=size), unit="D")

    ok = p[~is_failed]
    bad = p[is_failed]

    def make_events(rows: pd.DataFrame, status: str, event_at: pd.Series) -> pd.DataFrame:
        """One event per row in `rows`: same columns for every status."""
        return pd.DataFrame(
            {
                "payment_id": rows["payment_id"],
                "status": status,
                "event_at": event_at,
            }
        )

    pending = make_events(p, "pending_submission", p["charge_date"] - pd.Timedelta(days=5))
    submitted = make_events(p, "submitted", p["charge_date"] - pd.Timedelta(days=2))
    confirmed = make_events(ok, "confirmed", ok["charge_date"])
    paid_out = make_events(ok, "paid_out", ok["charge_date"] + random_days(1, 2, len(ok)))
    failed = make_events(bad, "failed", bad["charge_date"] + random_days(1, 4, len(bad)))

    events = pd.concat([pending, submitted, confirmed, paid_out, failed], ignore_index=True)
    events = events.sort_values(["payment_id", "event_at"]).reset_index(drop=True)
    events["event_id"] = [f"EV{i:07d}" for i in range(1, len(events) + 1)]

    events = events[events["event_at"] <= END_DATE]

    return events[
        [
            "event_id",
            "payment_id",
            "status",
            "event_at",
        ]
    ]


# ----------------------------------------------------------------------------------------------


def generate_all(n_customers: int, n_merchants: int) -> dict[str, pd.DataFrame]:
    """Generate the whole domain, parents before children."""
    rng = np.random.default_rng(SEED)
    Faker.seed(SEED)
    fake = Faker()

    merchants = generate_merchants(n_merchants, rng, fake)
    customers = generate_customers(n_customers, rng, fake)
    mandates = generate_mandates(customers, merchants, rng)

    check = mandates.merge(
        customers[["customer_id", "created_at"]],
        on="customer_id",
        how="left",
        suffixes=("_mandate", "_customer"),
    )
    assert (check["created_at_mandate"] >= check["created_at_customer"]).all(), (
        "mandate created before its customer!"
    )

    assert (
        mandates["cancelled_at"].isna() | (mandates["cancelled_at"] > mandates["created_at"])
    ).all()

    assert (mandates.loc[mandates["currency"] == "GBP", "scheme"] == "bacs").all()

    payments = generate_payments(mandates, rng)  # later
    events = generate_events(payments, rng)  # later
    latest = events.sort_values("event_at").groupby("payment_id")["status"].last()
    payments["status"] = payments["payment_id"].map(latest)

    payments.loc[payments["status"] != "failed", "failure_reason"] = None

    assert payments["mandate_id"].isin(mandates["mandate_id"]).all(), (
        "payments with unknown mandate_id!"
    )

    check_pm_mand = payments.merge(mandates, on="mandate_id", how="inner")[
        ["payment_id", "charge_date", "mandate_id", "created_at", "cancelled_at"]
    ]

    assert (check_pm_mand["charge_date"] >= check_pm_mand["created_at"]).all(), (
        "Charged before mandate created!"
    )

    assert (
        (check_pm_mand["charge_date"]
        < check_pm_mand["cancelled_at"]) & (check_pm_mand["charge_date"]
        < END_DATE)
    ).all(), "Charged after cancelled!"

    return {
        "merchants": merchants,
        "customers": customers,
        "mandates": mandates,
        "payments": payments,
        "events": events,
    }


# ---------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    result = generate_all(5, 3)
    for name, table in result.items():
        print(f"-- {name} " + "-" * 30)
        print(table)
        print()

    print(result["payments"]["status"].value_counts())
