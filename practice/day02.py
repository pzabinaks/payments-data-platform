from pathlib import Path
import csv

p = Path('data/raw/payments_raw.csv')


#Task  nr 1
file_size = p.stat().st_size
print (f"File size: {file_size/1024/1024} ")
print()

#task nr2
with open(p) as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        pass
print (f"Row count: {csv_reader.line_num} ")


#task nr3 and nr4
distinct_status_list = []
distinct_currency_list =[]
l_missing_payment_id  = 0
l_missing_Customer  = 0
l_missing_Merchant = 0
l_missing_Amount = 0
l_missing_currency = 0 
l_missing_status = 0
l_missing_date = 0 


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

        try:
            index = distinct_currency_list.index(row[4])
            #print("String found at index", index)
        except ValueError:
            distinct_currency_list.append(row[4])

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




# Data quality issues
# Upper lower case values for statuses
# Upper lower case values for currency
# Space symbol for some currency records ' EUR'
# missing items 