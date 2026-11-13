--backup original
create or replace table marts.fct_payments_original as select * from marts.fct_payments where charge_date>'1990-01-01';


---- TEST CASE #1   -- valid data, no exceptions 
call marts.p_reconcile_payments(DATE '2026-09-01');



-----  TEST  CASE #2 ----- amount mismatches
update marts.fct_payments trg
  set amount = amount + 10
where payment_id='PAY0429055'
 and  trg.charge_date >= '2026-09-01' and trg.charge_date< DATE_ADD('2026-09-01', INTERVAL 1 MONTH);

update marts.fct_payments trg 
  set amount = amount + 20
where payment_id='PAY0097880'
 and  trg.charge_date >= '2026-09-01' and trg.charge_date< DATE_ADD('2026-09-01', INTERVAL 1 MONTH);

call marts.p_reconcile_payments(DATE '2026-09-01');
--check  marts.recon_run_log and marts.recon_exceptions;


-----   TEST CASE #3 ----- count mismatches
DELETE FROM marts.fct_payments trg
WHERE trg.charge_date >= '2026-09-01' and trg.charge_date< DATE_ADD('2026-09-01', INTERVAL 1 MONTH)
  AND payment_id IN (
    SELECT payment_id
    FROM marts.fct_payments
    WHERE charge_date >= '2026-09-01' and charge_date< DATE_ADD('2026-09-01', INTERVAL 1 MONTH)
    LIMIT 10
  );

call marts.p_reconcile_payments(DATE '2026-09-01');
--check  marts.recon_run_log and marts.recon_exceptions;


-----    TEST CASE #4 -- take out one status for all period

delete  
from `marts.fct_payments` trg
where trg.charge_date >= '2026-09-01' and trg.charge_date< DATE_ADD('2026-09-01', INTERVAL 1 MONTH)
and status= 'charged_back';


call marts.p_reconcile_payments(DATE '2026-09-01');
--check  marts.recon_run_log and marts.recon_exceptions;


------------------------------------------------------------------------------------------------------------------------------------------------------------
--overall check by runs

select rl.run_id,rl.started_at,rl.finished_at,rl.check_month,rl.status,rl.exception_count,rd.status_value,rd.metric,rd.source_value,rd.target_value,rd.diff
from marts.recon_run_log rl
left join marts.recon_exceptions rd
  on rl.run_id = rd.run_id
order by started_at;
-------------------------------------------------------------------------------------------------------------------------------------------------------------


--restore data
truncate table marts.fct_payments;
insert into marts.fct_payments select * from marts.fct_payments_original; 