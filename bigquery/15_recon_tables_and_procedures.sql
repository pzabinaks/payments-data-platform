-- table holds reconcile runs
create or replace table marts.recon_run_log(run_id STRING DEFAULT (GENERATE_UUID()),
                                            started_at TIMESTAMP not null,
                                            finished_at TIMESTAMP,
                                            check_month DATE not null,
                                            status string not null, -- running / ok / differences / failed
                                            exception_count INT, 
                                            error_message STRING);

-- table holds iformation about particular checks for one reconcile run
create or replace table marts.recon_exceptions(run_id STRING,
                                              check_month DATE not null, 
                                              status_value string, --(the payment status compared), 
                                              metric string, --row_count,total_amount,status_match
                                              source_value NUMERIC, 
                                              target_value NUMERIC, 
                                              diff NUMERIC                                             
                                              );


-- Procedure to register reconcile run
CREATE OR REPLACE PROCEDURE marts.p_start_reconcile_run(
  IN i_check_month DATE,
  OUT o_generated_id STRING
)
BEGIN
  -- 1. Generate the unique ID first and store it in the OUT variable
  SET o_generated_id = GENERATE_UUID();

  -- 2. Insert the record into your target table using that ID
  INSERT INTO marts.recon_run_log (
    run_id,
    check_month,
    status,
    started_at
  )
  VALUES (
    o_generated_id,
    i_check_month,
    'running',
    CURRENT_TIMESTAMP()
  );
END;

CREATE OR REPLACE PROCEDURE marts.p_end_reconcile_run(
  IN i_run_id STRING,
  IN i_status STRING,
  IN i_run_error STRING,
  IN i_exception_count INT64
)
BEGIN
  UPDATE marts.recon_run_log
     SET status  = i_status
        ,error_message = i_run_error
        ,finished_at = CURRENT_TIMESTAMP()
        ,exception_count = i_exception_count
  WHERE run_id = i_run_id;
END;



CREATE OR REPLACE PROCEDURE marts.p_check_counts_per_status(
   IN i_run_id STRING,
   IN i_check_month DATE,
   OUT o_exception_count INT64  
   )
OPTIONS(strict_mode=false) -- to handle Cannot query.. without query on time of compilation
BEGIN  
   
   INSERT INTO marts.recon_exceptions(run_id ,
                                      check_month , 
                                      status_value , 
                                      metric , 
                                      source_value , 
                                      target_value , 
                                      diff  
                                      )
  select i_run_id,
         i_check_month,
         coalesce(src.status,trg.status),
         'row_count',
         COALESCE(src.cnt, 0),
         COALESCE(trg.cnt, 0),
         COALESCE(src.cnt, 0) - COALESCE(trg.cnt, 0)
FROM (
  SELECT status, COUNT(1) AS cnt
  FROM raw.payments
  WHERE DATE(charge_date) >= i_check_month and DATE(charge_date)< DATE_ADD(i_check_month, INTERVAL 1 MONTH)
  GROUP BY status
) src
FULL OUTER JOIN (
  SELECT status, COUNT(1) AS cnt
  FROM marts.fct_payments trg
  WHERE trg.charge_date >= i_check_month and trg.charge_date< DATE_ADD(i_check_month, INTERVAL 1 MONTH)
  GROUP BY status
) trg
  ON src.status = trg.status
WHERE COALESCE(src.cnt, 0) <> COALESCE(trg.cnt, 0);

SET o_exception_count = @@row_count;

END;  

CREATE OR REPLACE PROCEDURE marts.p_check_sums_per_status(
   IN i_run_id STRING,
   IN i_check_month DATE,
   OUT o_exception_count INT64  
   )
OPTIONS(strict_mode=false) -- to handle Cannot query.. without query on time of compilation
BEGIN  
   
   INSERT INTO marts.recon_exceptions(run_id ,
                                      check_month , 
                                      status_value , 
                                      metric , 
                                      source_value , 
                                      target_value , 
                                      diff  
                                      )
  select i_run_id,
         i_check_month,
         trg.status,
         'total_amount',
         src.amt,
         trg.amt,
         src.amt - trg.amt
  from (select  sum(amount) amt,  status
        from marts.fct_payments trg
       where trg.charge_date >= i_check_month and trg.charge_date< DATE_ADD(i_check_month, INTERVAL 1 MONTH)
        group by status
     ) trg
 join (select  sum(cast(trg.amount as numeric) ) amt, status
        from raw.payments trg
       where DATE(charge_date) >= i_check_month and DATE(charge_date)< DATE_ADD(i_check_month, INTERVAL 1 MONTH)
        group by status) src
   on trg.status=src.status
where trg.amt<>src.amt;

SET o_exception_count = @@row_count;

END;


CREATE OR REPLACE PROCEDURE marts.p_reconcile_payments(i_check_month DATE)
BEGIN
  DECLARE v_exceptions      INT64 DEFAUlT 0;
  DECLARE v_exceptions_all  INT64 DEFAUlT 0;
  DECLARE v_run_id          STRING;
  DECLARE v_err_message     STRING;

  call marts.p_start_reconcile_run(
         i_check_month
        ,v_run_id 
       );
  
  BEGIN
    --check counts
    call marts.p_check_counts_per_status(
           v_run_id
          ,i_check_month
          ,v_exceptions
         );
    SET v_exceptions_all = v_exceptions_all + v_exceptions;
    --check sums
    call marts.p_check_sums_per_status(
           v_run_id
          ,i_check_month
          ,v_exceptions
         );
    SET v_exceptions_all = v_exceptions_all + v_exceptions;    
    
    --check statuses
    -- to be done


    IF v_exceptions_all=0 THEN
      --All good
      call marts.p_end_reconcile_run(
             v_run_id
            ,'ok'
            ,null 
            ,0
           );   
    ELSE
      -- Exceptions
      call marts.p_end_reconcile_run(
             v_run_id
            ,'differences'
            ,null 
            ,v_exceptions_all
           );         
    END IF; 
  EXCEPTION WHEN ERROR 
  THEN 
    SET v_err_message = @@error.message;
    call marts.p_end_reconcile_run(
           v_run_id
          ,'failed'
          ,v_err_message
          ,null 
         );
  END;

END;