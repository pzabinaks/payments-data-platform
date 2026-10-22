import pandas as pd

df = pd.read_parquet("data/clean/payments.parquet")
paid = df[df["status"] == "paid"]  # used by most tasks


# Task #1  ----------------------------------------------------

# SELECT merchant, COUNT(*) AS payments, SUM(amount) AS total
# FROM paid GROUP BY merchant ORDER BY total DESC;

# tips.groupby("sex")["total_bill"].count()
task_1 = paid.groupby("merchant").agg(payments=("payment_id", "count"), total=("amount", "sum")).sort_values(["total"],ascending=False)
print(task_1)

#NOTES - we should create function to calculate all in one curency before agregation


# Task #2  ----------------------------------------------------

# SELECT merchant, AVG(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failure_rate
# FROM payments GROUP BY merchant ORDER BY failure_rate DESC;

# tips.groupby("sex")["total_bill"].count()
task_2 = paid.groupby("merchant").agg(failure_rate=(paid["status"].case_when(
                                                                            [
                                                                            (paid["status"] == "failed", 1),
                                                                            (paid["status"] != "failed", 0),
                                                                            ] 
                                                                            ), "ment")).sort_values(["failure_rate"],ascending=False)
print(task_2)

#NOTES - we should create function to calculate all in one curency before agregation