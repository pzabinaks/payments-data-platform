import pandas as pd
import json

with open("data/raw/fx/fx_rates_2026-01-01_2026-10-15.json", encoding="utf-8") as f:
    rates = pd.DataFrame(json.load(f))


payments_all  = pd.read_parquet("data/clean/payments.parquet")
payments_paid = payments_all[payments_all["status"] == "paid"]


# Task #1  ----------------------------------------------------

# SELECT merchant, COUNT(*) AS payments, SUM(amount) AS total
# FROM payments_paid GROUP BY merchant ORDER BY total DESC;

# tips.groupby("sex")["total_bill"].count()
task_1 = (
    payments_paid.groupby("merchant")
    .agg(payments=("payment_id", "count"), total=("amount", "sum"))
    .sort_values(["total"], ascending=False)
)
print(task_1)
print()
# NOTES - we should create function to calculate all in one curency before agregation


# Task #2  ----------------------------------------------------

# SELECT merchant, AVG(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failure_rate
# FROM payments GROUP BY merchant ORDER BY failure_rate DESC;

# tips.groupby("sex")["total_bill"].count()
task_2 = (
    payments_all.assign(
        is_failed=payments_all["status"].case_when(
            [
                (payments_all["status"] == "failed", 1),
                (payments_all["status"] != "failed", 0),
            ]
        )
    )
    .groupby("merchant")
    .agg(failure_rate=("is_failed", "mean"))
    .sort_values(["failure_rate"], ascending=False)
)
print(task_2)
print()

# Task #3  ---------------------------------------------------
# SELECT DATE_TRUNC('month', created_at) AS month,
#       SUM(amount) FILTER (WHERE currency = 'EUR') AS eur,
#        SUM(amount) FILTER (WHERE currency = 'GBP') AS gbp
# FROM payments_paid GROUP BY 1 ORDER BY 1;

# Hint: payments_paid["created_at"].dt.to_period("M") gives the month, then pivot_table(index=..., columns="currency", values="amount", aggfunc="sum").

task_3 = (
    payments_paid.assign(month=payments_paid["created_at"].dt.to_period("M"))
    .pivot_table(index="month", columns="currency", values="amount", aggfunc="sum")
    .sort_values(["month"], ascending=True)
)

print(task_3)
print()

# Task #4  ---------------------------------------------------
# SELECT * FROM (
#   SELECT merchant, customer_id, SUM(amount) AS total,
#          ROW_NUMBER() OVER (PARTITION BY merchant ORDER BY SUM(amount) DESC) AS rn
#   FROM payments_paid WHERE customer_id <> 'UNKNOWN'
#   GROUP BY merchant, customer_id
# ) WHERE rn <= 3;


# groupby([...], as_index=False)["amount"].sum(), then groupby("merchant")["amount"].rank(method="first", ascending=False) is your ROW_NUMBER().

totals = (
    payments_paid[payments_paid["customer_id"] != "UNKNOWN"]
    .groupby(["merchant", "customer_id"], as_index=False)["amount"]
    .sum()
)

totals["rn"] = totals.groupby("merchant")["amount"].rank(method="first", ascending=False)

task_4 = totals[totals["rn"] <= 3]

print(task_4)
print()


# Task #5  ---------------------------------------------------
# SELECT day, SUM(amount) AS daily, SUM(SUM(amount)) OVER (ORDER BY day) AS running_total
# FROM payments_paid GROUP BY day;


daily = payments_paid.groupby(payments_paid["created_at"].dt.date)["amount"].sum()
running_total = daily.cumsum()

task_5 = pd.DataFrame({"daily": daily, "running_total": daily.cumsum()})
print(task_5.head())
print(task_5.tail())   
print()




# Task #6  ---------------------------------------------------
# SELECT customer_id, payment_id, created_at,
#        LAG(created_at) OVER (PARTITION BY customer_id ORDER BY created_at) AS prev_payment,
#        created_at - prev_payment AS gap
# FROM payments WHERE customer_id <> 'UNKNOWN';

payments_paid_known = payments_all[(payments_all["customer_id"] != "UNKNOWN")].copy()


ordered_payments = payments_paid_known.sort_values(by=["customer_id", "created_at"])

ordered_payments["prev_payment"] = ordered_payments.groupby("customer_id")["created_at"].shift(1)

ordered_payments["gap"] = (ordered_payments["created_at"] - ordered_payments["prev_payment"]).dt.total_seconds() / 3600
print(ordered_payments)
print()




# Task #7  ---------------------------------------------------
rates_gbp = rates[rates["quote"] == "GBP"].copy()

rates_gbp["created_at"] = pd.to_datetime(rates_gbp["date"])

rates_gbp_ordered = rates_gbp.sort_values(["created_at"], ascending=True)

payments_gbp = payments_paid[payments_paid["currency"] == "GBP"].sort_values("created_at")


all_in_eur = pd.merge_asof(payments_gbp, rates_gbp_ordered, on="created_at", direction="backward")

all_in_eur["amount_eur"] = all_in_eur["amount"] / all_in_eur["rate"]
print(f"GBP->EUR total (pandas): {all_in_eur['amount_eur'].sum():,.2f}")

print(all_in_eur["rate"].isna().sum()) 