import pandas as pd

df = pd.read_parquet("data/clean/payments.parquet")
paid = df[df["status"] == "paid"]  # used by most tasks


# Task #1  ----------------------------------------------------

# SELECT merchant, COUNT(*) AS payments, SUM(amount) AS total
# FROM paid GROUP BY merchant ORDER BY total DESC;

# tips.groupby("sex")["total_bill"].count()
task_1 = (
    paid.groupby("merchant")
    .agg(payments=("payment_id", "count"), total=("amount", "sum"))
    .sort_values(["total"], ascending=False)
)
print(task_1)

# NOTES - we should create function to calculate all in one curency before agregation


# Task #2  ----------------------------------------------------

# SELECT merchant, AVG(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failure_rate
# FROM payments GROUP BY merchant ORDER BY failure_rate DESC;

# tips.groupby("sex")["total_bill"].count()
task_2 = (
    df.assign(
        is_failed=df["status"].case_when(
            [
                (df["status"] == "failed", 1),
                (df["status"] != "failed", 0),
            ]
        )
    )
    .groupby("merchant")
    .agg(failure_rate=("is_failed", "mean"))
    .sort_values(["failure_rate"], ascending=False)
)
print(task_2)


# Task #3  ---------------------------------------------------
# SELECT DATE_TRUNC('month', created_at) AS month,
#       SUM(amount) FILTER (WHERE currency = 'EUR') AS eur,
#        SUM(amount) FILTER (WHERE currency = 'GBP') AS gbp
# FROM paid GROUP BY 1 ORDER BY 1;

# Hint: paid["created_at"].dt.to_period("M") gives the month, then pivot_table(index=..., columns="currency", values="amount", aggfunc="sum").

task_3 = paid.assign(month=paid["created_at"].dt.to_period("M")).pivot_table(
    index="month", columns="currency", values="amount", aggfunc="sum"
).sort_values(["month"], ascending=False)

print(task_3)


# Task #4  ---------------------------------------------------
# SELECT * FROM (
#   SELECT merchant, customer_id, SUM(amount) AS total,
#          ROW_NUMBER() OVER (PARTITION BY merchant ORDER BY SUM(amount) DESC) AS rn
#   FROM paid WHERE customer_id <> 'UNKNOWN'
#   GROUP BY merchant, customer_id
# ) WHERE rn <= 3;


#groupby([...], as_index=False)["amount"].sum(), then groupby("merchant")["amount"].rank(method="first", ascending=False) is your ROW_NUMBER().

task_4 = paid.assign(
         total = paid["customer_id" != 'UNKNOWN'].groupby(["merchant,customer_id"], as_index=False)["amount"].sum() ,
         row_num = paid.groupby("merchant")["amount"].rank(method="first", ascending=False)
        )
