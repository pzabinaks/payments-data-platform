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


# generate_mandates(customers, merchants, rng): each customer gets 1–3 mandates with random merchants. Scheme follows the customer’s country: GB → bacs / GBP, otherwise sepa_core / EUR.
# About 10% are cancelled, with a cancelled_at after created_at. A mandate can’t start before the customer exists.

# "mandate_id"
# "customer_id"
# "merchant_id"
# "scheme",
# "currency",
# "status",
# "created_at",
# "cancelled_at",


def generate_mandates(
    customers: pd.DataFrame,
    merchants: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:

    n_per_customer = rng.integers(
        1, MAX_MANDATES+1, size=len(customers)
    )  # 1, 2 or MAX_MANDATES mandates per customer
    m = customers.loc[customers.index.repeat(n_per_customer)].reset_index(drop=True)
    m = m.rename(columns={"created_at": "customer_created_at"})  # rename column

    n = len(m)
    m["mandate_id"] = [f"MD{i:07d}" for i in range(1, n + 1)]
    m["merchant_id"] = rng.choice(merchants["merchant_id"], size=n)

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

    # payments = generate_payments(mandates, rng)          # later
    # events = generate_events(payments, rng)              # later

    return {
        "merchants": merchants,
        "customers": customers,
        "mandates": mandates,
        # "payments": payments,
        # "events": events,
    }


result = generate_all(10, 5)
