from pathlib import Path
import csv
from datetime import datetime
import pandas as pd

p = Path('data/raw/payments_raw.csv')


#Task  nr 1
file_size = p.stat().st_size
print (f"File size: {file_size/1024/1024} ")
print()

#task nr2
with open(p) as f:
    csv_reader = csv.reader(f)
    next(csv_reader) # Skip the header row if your file has one
    for row in csv_reader:
        pass
print (f"Row count: {csv_reader.line_num} ")


#task nr3 and nr4
distinct_status_list = []
distinct_currency_list =[]

payments = set()
duplicate_payments =[]

wrong_amounts = []
wrong_dates = []
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

l_missing_payment_id  = 0
l_missing_Customer  = 0
l_missing_Merchant = 0
l_missing_Amount = 0
l_missing_currency = 0 
l_missing_status = 0
l_missing_date = 0 

with open(p, newline="", encoding="utf-8") as f:
    header = next(csv.reader(f))
print(header)          # a list, so repr() is applied automatically


with open(p) as f:
    csv_reader = csv.reader(f)
    next(csv_reader) # Skip the header row if your file has one
    for row in csv_reader:
        if row[0] == '':
            l_missing_payment_id+= 1

        if row[1] == '':
            l_missing_Customer+= 1

        if row[2] == '':
            l_missing_Merchant+= 1

        if row[3] == '':
            l_missing_Amount+= 1

        if row[4] == '':
            l_missing_currency+= 1

        if row[5] == '':
            l_missing_status+= 1          

        if row[6] == '':
            l_missing_date+= 1     

        try:
            index = distinct_status_list.index(row[5])
            #print("String found at index", index)
        except ValueError:
            distinct_status_list.append(row[5])

         #payemnt uniqueness check - payment id is a PK, must be unique
        if row[0] in payments:
            duplicate_payments.append(row[0])   
        else:
            payments.add(row[0])            

        try:
            index = distinct_currency_list.index(row[4])
            #print("String found at index", index)
        except ValueError:
            distinct_currency_list.append(row[4])

        try:
            # I believe , is fine as decimal sign too
            number = float(row[3].replace(',', '.'))
        except ValueError:
            wrong_amounts.append(row[3])

        # Lets check date format
        try:
            valid_date = datetime.strptime(row[6], DATE_FORMAT)
        except ValueError:
             wrong_dates.append(row[6])
                

for status in sorted(distinct_status_list):
    print(repr(status))

#        if row['Status'] not in distinct_list:
#            distinct_list.append(row['Status'])
print (f"Distinct statuses: {distinct_status_list}")
print (f"Distinct currencies: {distinct_currency_list}")

print("Missing items")

print (f"l_missing_payment_id: {l_missing_payment_id}")
print (f"l_missing_Customer: {l_missing_Customer}")
print (f"l_missing_Merchant: {l_missing_Merchant}")
print (f"l_missing_Amount: {l_missing_Amount}")
print (f"l_missing_currency: {l_missing_currency}")
print (f"l_missing_status: {l_missing_status}")
print (f"l_missing_date: {l_missing_date}")


print (f"Invalid amounts: {wrong_amounts}")
#print (f"Invalid dates: {wrong_dates}")
#print (f"Invalid date count: {len(set(wrong_dates))}")
#print (f"Duplicate payments: {duplicate_payments}") 


# Data quality issues
# Upper lower case values for statuses
# Upper lower case values for currency
# Space symbol for some currency records ' EUR'
# missing items - customers
# wrong date formats
# leading space for Status
# payment id is not unique

def clean_column_names(df):
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df.rename(columns={"customer": "customer_id"})

def clean_amount(df):
    df["amount"] = df["amount"].str.replace(",", ".").astype(float)
    return df

def clean_currency(df):
    df["currency"] = df["currency"].str.upper().astype("category")
    return df

def clean_status(df):
    df["status"] = df["status"].str.strip().str.lower().astype("category")
    return df

def clean_dates(df):
    df["created_at"] = pd.to_datetime(df["created_at"], format="mixed", dayfirst=True)
    return df

def remove_duplicates(df):
    return df.drop_duplicates()

def fill_unknown_customer(df):
    df["customer_id"] = df["customer_id"].fillna("UNKNOWN")
    return df

df = pd.read_csv(p)
#print(df.columns.tolist())      # BEFORE: ['Payment ID', ' Customer ', 'Merchant', 'Amount', ...]
overall_records = len(df)

df = clean_column_names(df)     # step 1: always first
print(df.columns.tolist())      # AFTER:  ['payment_id', 'customer_id', 'merchant', 'amount', ...]

df = clean_amount(df)           # step 2: can now use the clean name
df = clean_status(df)
df = clean_currency(df)
df = clean_dates(df)
df = remove_duplicates(df)

duplicates_removed = overall_records - len(df)

df = fill_unknown_customer(df)

unknown_customers = df.loc[df["customer_id"] == "UNKNOWN", "customer_id"].count()
paid_total = df.loc[df["status"] == "paid", "amount"].sum()

#print(len(df)) 
print (f"rows read:           {overall_records}")    
print (f"duplicates removed:  {duplicates_removed}")        
print (f"missing customer:    {unknown_customers}")
print (f"rows written:        {overall_records - duplicates_removed}")   
print (f"Paid total:          {paid_total:.2f}")

#df.info()                       # amount should now show as float64



out = Path("data/clean")
out.mkdir(parents=True, exist_ok=True)
df.to_csv(out / "payments.csv", index=False)
df.to_json(out / "payments.json", orient="records", lines=True, date_format="iso")
df.to_parquet(out / "payments.parquet", index=False)

for f in sorted(out.iterdir()):
    print(f"{f.name:20} {f.stat().st_size / 1024 / 1024:.2f} MB")

pd.read_parquet(out / "payments.parquet").info()   # types survive
pd.read_csv(out / "payments.csv").info()           # types l