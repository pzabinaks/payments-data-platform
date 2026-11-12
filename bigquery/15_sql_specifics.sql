--Task 1
SELECT
  payment_id,
  event_id,
  event_at,
  status
FROM raw.events
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY payment_id 
  ORDER BY event_at DESC,event_id DESC
) = 1;

--Task 2
create or replace table marts.payment_history
as
with events as (select ARRAY_AGG(STRUCT(status,event_at) ORDER BY event_at,event_id) as events,payment_id from raw.events a  GROUP BY payment_id)
select p.payment_id,
       p.mandate_id,
       p.customer_id,
       p.merchant_id,
       p.charge_date,
       p.amount,
       p.currency,
       p.status,
       p.failure_reason,
       e.events
  from marts.fct_payments p
  left join events e
    on p.payment_id=e.payment_id
  where charge_date>'1999-01-01'; -- to fullfill partition filering


--Task 3.1 event count for payment
select payment_id, ARRAY_LENGTH(events)
from marts.payment_history;

--Task 3.2 payemtns having event 'charged_back'
select payment_id
from marts.payment_history,
where exists (select 1 from UNNEST(events) where status='charged_back');


--Task 3.3 array to rows
 --  count(1) -- 3884020 count matches with raw.events
select payment_id,event.status,event.event_at
from marts.payment_history,
UNNEST(events) AS event;


--Task 4: MERGE: keep a “current status” table up to date.
--4.1 create initial table
create or replace table marts.payment_status_current
as 
SELECT
  payment_id,
  event_at,
  status
FROM raw.events
where date(event_at) <'2026-09-30'
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY payment_id 
  ORDER BY event_at DESC,event_id DESC
) = 1;



-- test data
select *
from (
select payment_id,sum(case when date(event_at)<'2026-09-30' then 1 else 0 end) before,
sum(case when date(event_at) >= '2026-09-30' then 1 else 0 end) after
FROM raw.events
group by payment_id
)
where before<>0 and after<>0
limit 10;

select *
from raw.events
where payment_id= 'PAY0496743'; -- example payment having before and after dates

select *
from marts.payment_status_current
where payment_id= 'PAY0496743';  

--before merge: --2026-09-16 paid_out     after merge:   2026-09-30 charged_back
-- end tests 



--4.2 MERGE statement itself
MERGE marts.payment_status_current AS target
USING (
SELECT
  payment_id,
  event_at,
  status
FROM raw.events
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY payment_id 
  ORDER BY event_at DESC ,event_id DESC
) = 1
) AS source
ON target.payment_id = source.payment_id 

-- Update existing records when matched
WHEN MATCHED AND source.status <> target.status THEN 
  UPDATE SET
    target.status = source.status,
    target.event_at = source.event_at

-- Insert new records when not found in target
WHEN NOT MATCHED BY TARGET THEN
  INSERT (payment_id, event_at, status)
  VALUES (source.payment_id, source.event_at, source.status);
