from collections import defaultdict

payments = [
    {"id": 1, "customer": "A", "amount": 120.0, "status": "paid"},
    {"id": 2, "customer": "B", "amount": 75.5,  "status": "failed"},
    {"id": 3, "customer": "A", "amount": 30.0,  "status": "paid"},
    {"id": 4, "customer": "C", "amount": 200.0, "status": "paid"},
    {"id": 5, "customer": "B", "amount": 75.5,  "status": "paid"},
]

# 1. SELECT * FROM payments WHERE status = 'paid'          -> list comprehension
print("#1")
paid = [p for p in payments if p["status"] == "paid"]
print (paid)
print('\n')


# 2. SELECT SUM(amount) FROM payments WHERE status='paid'  -> sum() + generator
print("#2")
paid = sum([p["amount"] for p in payments if p["status"] == "paid"])
print (paid)
print('\n')


# 3. SELECT customer, SUM(amount) ... GROUP BY customer    -> dict
print("#3")
groups = defaultdict(list)
for p in payments:
    groups[p["customer"]].append(p["amount"])

result = {key: sum(value) for key, value in groups.items()}
print(dict(result))
print('\n')


# 4. SELECT DISTINCT customer
print("#4")                             
distinct_customers = list({item["customer"] for item in payments})

print(distinct_customers)
print('\n')

# 5. ORDER BY amount DESC, take top 2                      -> sorted() with key=
print("#5")
b = sorted(payments, key=lambda x: x['amount'],reverse=True)[:2]
print(b)
print()

# 6. Failure rate per customer (failed / total)            -> combine the above

print("#6")
total_count = {}
failed_count = {}

# 1. Populate the counts using standard dictionaries
for p in payments:
    c = p["customer"]
    
    # Increment total count
    total_count[c] = total_count.get(c, 0) + 1
    
    # Increment failed count only if status is failed
    if p["status"] == "failed":
        failed_count[c] = failed_count.get(c, 0) + 1


failure_rates = {}
for c in total_count:
    failures = failed_count.get(c, 0)  
    total = total_count[c]
    
    failure_rates[c] = round(failures / total, 2)

# 3. Sort the final result by key
sorted_results = dict(sorted(failure_rates.items()))
print(sorted_results)
print()

# 7. Write a function summarize(payments) that returns tasks 3 and 6 as one dict
print("#7")
def summarize(payments):
    groups = defaultdict(list)
    for p in payments:
        groups[p["customer"]].append(p["amount"])

    totals = {key: sum(value) for key, value in groups.items()}
    
    # ... code from #6 -> failure_rates
    total_count = {}
    failed_count = {}

    # 1. Populate the counts using standard dictionaries
    for p in payments:
        c = p["customer"]
    
        # Increment total count
        total_count[c] = total_count.get(c, 0) + 1
    
        # Increment failed count only if status is failed
        if p["status"] == "failed":
            failed_count[c] = failed_count.get(c, 0) + 1


    failure_rates = {}
    for c in total_count:
        failures = failed_count.get(c, 0)  
        total = total_count[c]
    
        failure_rates[c] = round(failures / total, 2)   
    
    
    return {"totals": totals, "failure_rate": failure_rates}

print(summarize(payments))