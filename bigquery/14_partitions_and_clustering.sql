create table marts.fct_payments_nopart as
select p.payment_id,
       m.mandate_id,
       m.customer_id,
       m.merchant_id,
       date(p.charge_date) as charge_date,
       cast(p.amount as numeric) as amount,
       p.currency,
       p.status,
       p.failure_reason
from raw.payments p
join raw.mandates m
  on p.mandate_id = m.mandate_id;




select  count(1)
from marts.fct_payments_nopart;

-- 1653
select avg(count_1)
from (
select count(1) as count_1 ,charge_date
from marts.fct_payments_nopart
group by charge_date
);



-- 45032
select avg(count_1)
from (
select count(1) as count_1 ,DATE_TRUNC(charge_date, MONTH) as charge_month
from marts.fct_payments_nopart
group by DATE_TRUNC(charge_date, MONTH) 
);




--- Partitioned table -  as we have avarage 45k payments in a month it is reasonable to partition it by month
create table marts.fct_payments 
PARTITION BY
  DATE_TRUNC(charge_date, MONTH)
CLUSTER BY
  merchant_id
as
select p.payment_id,
       m.mandate_id,
       m.customer_id,
       m.merchant_id,
       date(p.charge_date) as charge_date,
       cast(p.amount as numeric) as amount,
       p.currency,
       p.status,
       p.failure_reason
from raw.payments p
join raw.mandates m
  on p.mandate_id = m.mandate_id;


SELECT partition_id, total_rows
FROM marts.INFORMATION_SCHEMA.PARTITIONS
WHERE table_name = 'fct_payments'
ORDER BY partition_id;



--                                          |est. b no partition |act. b no partition | est. b partition |act. b  partition       
----------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------
-- 1. total amount for september 2026          22.68 MB              22.68 MB           1.75  MB             1.75  MB
----------------------------------------------------------------------------------------------------------------------------------------
-- 2. total amount for one merchant            24.57 MB              24.57 MB           24.57 MB             24.56 MB            
----------------------------------------------------------------------------------------------------------------------------------------
-- 3. one merchant in one month                32.1 MB               32.1 MB            2.47 MB              2.47 MB        


--1 nopart
select sum(amount)
from marts.fct_payments_nopart
where DATE_TRUNC(charge_date, MONTH) = DATE('2026-09-01');

--1 part
select sum(amount)
from marts.fct_payments
where DATE_TRUNC(charge_date, MONTH) = DATE('2026-09-01');

--2 nopart
select sum(amount)
from marts.fct_payments_nopart
where merchant_id ='MER00002';

--2 part
select sum(amount)
from marts.fct_payments
where merchant_id ='MER00002';

--3 nopart
select sum(amount)
from marts.fct_payments_nopart
where merchant_id ='MER00002'
and DATE_TRUNC(charge_date, MONTH) = DATE('2026-09-01');

--3 part
select sum(amount)
from marts.fct_payments
where merchant_id ='MER00002'
and DATE_TRUNC(charge_date, MONTH) = DATE('2026-09-01');

-- add mandatory filter for partition 
ALTER TABLE marts.fct_payments
SET OPTIONS (
  require_partition_filter = true
);

-- now it is not allowed to unfilter by partition
-- Example if only filtering by merchant_id: Cannot query over table 'marts.fct_payments' without a filter over column(s) 'charge_date' that can be used for partition elimination