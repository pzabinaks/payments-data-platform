--# FCT_PAYMENTS    -------------------------------------------------------------------------------------

DROP TABLE IF EXISTS fct_payments;


CREATE TABLE fct_payments(
     payment_id_sk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY
    ,payment_id text  NOT NULL --payment_id from payements
    ,charge_date_sk integer   -- FK to dim_date
    ,customer_sk  integer     -- FK to dim_customer
    ,merchant_sk  integer     -- FK to dim_merchant
    ,mandate_sk   integer     -- FK to mandate
    ,submitted_date_sk    integer   -- FK to dim_date
    ,confirmed_date_sk    integer   -- FK to dim_date
    ,paid_out_date_sk     integer   -- FK to dim_date
    ,failed_date_sk       integer   -- FK to dim_date
    ,charged_back_date_sk integer   -- FK to dim_date
    ,amount         numeric(12, 2)  -- amount (measure)
    ,status         text   -- status of the payment
    ,failure_reason text   -- failure reason
    ,is_failed   integer   -- additive: 0- false 1- true
    ,is_charged_back      integer   -- additive: 0- false 1- true
    ,days_to_payout       integer     -- additive: paid_out_date − submitted_date
    ,days_to_charge_back  integer  -- days till money charged back  
    ,currency text                 -- Currency
    ,amount_eur    numeric(12, 2) -- calculated amount in eur by currency  
);


insert into fct_payments(
    payment_id
    ,charge_date_sk
    ,customer_sk
    ,merchant_sk
    ,mandate_sk
    ,submitted_date_sk
    ,confirmed_date_sk
    ,paid_out_date_sk
    ,failed_date_sk
    ,charged_back_date_sk
    ,amount
    ,status
    ,failure_reason
    ,is_failed
    ,is_charged_back
    ,days_to_payout
    ,days_to_charge_back
    ,currency
    ,amount_eur 
)
select stg_pay.payment_id
      ,dim_dat.date_sk as charge_date_sk
      ,dim_cus.customer_sk as customer_sk
      ,dim_mer.merchant_sk as merchant_sk
      ,dim_man.mandate_sk as mandate_sk
      ,stg_dim_dates.submitted_dt_sk as submitted_date_sk
      ,stg_dim_dates.confirmed_dt_sk as confirmed_date_sk
      ,stg_dim_dates.paid_out_dt_sk as paid_out_date_sk 
      ,stg_dim_dates.failed_dt_sk as failed_date_sk
      ,stg_dim_dates.charged_back_dt_sk as charged_back_date_sk
      ,stg_pay.amount as amount 
      ,stg_pay.status as status
      ,stg_pay.failure_reason as failure_reason
      ,case when stg_pay.status='failed' then 1 else 0 end as is_failed
      ,case when stg_pay.status='charged_back' then 1 else 0 end as is_charged_back
      ,stg_dim_dates.paid_out_dt - stg_dim_dates.submitted_dt as  days_to_payout
      ,stg_dim_dates.charged_back_dt - stg_dim_dates.paid_out_dt as days_to_charge_back
      ,stg_pay.currency
      ,round(stg_pay.amount / coalesce(r.rate,1),2) as  amount_eur 
from stg_payments as stg_pay
 join stg_mandates as stg_man
   on (stg_pay.mandate_id = stg_man.mandate_id)
 join dim_mandate  as dim_man
   on stg_pay.mandate_id = dim_man.mandate_id
 join dim_merchant dim_mer
   on (dim_mer.merchant_id = stg_man.merchant_id)
 join dim_customer dim_cus 
   on (dim_cus.customer_id  = stg_man.customer_id) 
 join dim_date dim_dat
   on (stg_pay.charge_date::date = dim_dat.calendar_date)
 join (select stg_eve.payment_id
             ,conf_dt.date_sk as confirmed_dt_sk
             ,failed_dt.date_sk as failed_dt_sk
             ,paid_out_dt.date_sk as paid_out_dt_sk
             ,pending_submission_dt.date_sk as pending_submission_dt_sk
             ,submitted_dt.date_sk as submitted_dt_sk
             ,charged_back_dt.date_sk as charged_back_dt_sk
             ,paid_out_dt
             ,charged_back_dt
             ,submitted_dt
         from (select payment_id
                      ,min(case when status = 'confirmed' then event_at end)::date as confirmed_dt
                      ,min(case when status = 'failed' then event_at end)::date as failed_dt
                      ,min(case when status = 'paid_out' then event_at end)::date as paid_out_dt
                      ,min(case when status = 'pending_submission' then event_at end)::date as pending_submission_dt
                      ,min(case when status = 'submitted' then event_at end)::date as submitted_dt
                      ,min(case when status = 'charged_back' then event_at end)::date as charged_back_dt
                from stg_events
            group by payment_id
            ) stg_eve
        left join dim_date as conf_dt
          on (stg_eve.confirmed_dt = conf_dt.calendar_date)
        left join dim_date as failed_dt
          on (stg_eve.failed_dt = failed_dt.calendar_date)
        left join dim_date as paid_out_dt
          on (stg_eve.paid_out_dt = paid_out_dt.calendar_date)  
        left join dim_date as pending_submission_dt
          on (stg_eve.pending_submission_dt = pending_submission_dt.calendar_date)  
        left join dim_date as submitted_dt
          on (stg_eve.submitted_dt = submitted_dt.calendar_date)
        left join dim_date as charged_back_dt
          on (stg_eve.charged_back_dt = charged_back_dt.calendar_date)  
      ) stg_dim_dates
        on (stg_dim_dates.payment_id = stg_pay.payment_id)
left join lateral 
  (select *
  from fx_rates rates
   where  stg_pay.currency = rates.quote and rates.rate_date <= stg_pay.charge_date::date
   ORDER BY rates.rate_date DESC LIMIT 1
  )r ON true;
--limit 10;