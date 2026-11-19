with stg_payments as (

    select * from {{ ref('stg_payments') }}

),

stg_mandates as (

    select * from {{ ref('stg_mandates') }}

),

dim_dates as (
    select * from {{ref('dim_dates')}}
),

dim_customers as (
    select * from {{ref('dim_customers')}}
),

dim_mandates as (
    select * from {{ref('dim_mandates')}}
),

dim_merchants as (
    select * from {{ref('dim_merchants')}}
),

int_payment_milestones as (
    select * from {{ref('int_payment_milestones')}}
),


final as (

    select
        {{ dbt_utils.generate_surrogate_key(['stg_pay.payment_id']) }} as payment_sk
          ,stg_pay.payment_id
          ,stg_pay.charge_date
          ,dim_dat.date_sk as charge_date_sk
          ,dim_cus.customer_sk as customer_sk
          ,dim_mer.merchant_sk as merchant_sk
          ,stg_man.merchant_id
          ,dim_man.mandate_sk as mandate_sk
          ,stg_dim_dates.submitted_dt_sk as submitted_date_sk
          ,stg_dim_dates.confirmed_dt_sk as confirmed_date_sk
          ,stg_dim_dates.paid_out_dt_sk as paid_out_date_sk 
          ,stg_dim_dates.failed_dt_sk as failed_date_sk
          ,stg_dim_dates.charged_back_dt_sk as charged_back_date_sk
          ,stg_dim_dates.pending_submission_dt_sk as pending_submission_date_sk
          ,stg_pay.amount as amount 
          ,stg_pay.status as status
         ,stg_pay.failure_reason as failure_reason
         ,case when stg_dim_dates.failed_at is not null then 1 else 0 end as is_failed
         ,case when stg_dim_dates.charged_back_at is not null then 1 else 0 end as is_charged_back
         ,stg_dim_dates.paid_out_at - stg_dim_dates.submitted_at as  days_to_payout
         ,stg_dim_dates.charged_back_at - stg_dim_dates.paid_out_at as days_to_charge_back
         ,stg_pay.currency
   from stg_payments as stg_pay
   join stg_mandates as stg_man
     on (stg_pay.mandate_id = stg_man.mandate_id)
   join dim_mandates  as dim_man
     on stg_pay.mandate_id = dim_man.mandate_id
   join dim_merchants dim_mer
     on (dim_mer.merchant_id = stg_man.merchant_id)
   join dim_customers dim_cus 
     on (dim_cus.customer_id  = stg_man.customer_id) 
   join dim_dates dim_dat
     on (stg_pay.charge_date = dim_dat.calendar_date)
 left join (select stg_eve.payment_id
             ,conf_dt.date_sk as confirmed_dt_sk
             ,failed_dt.date_sk as failed_dt_sk
             ,paid_out_dt.date_sk as paid_out_dt_sk
             ,submitted_dt.date_sk as submitted_dt_sk
             ,charged_back_dt.date_sk as charged_back_dt_sk
             ,pending_submission_dt.date_sk as pending_submission_dt_sk
             ,stg_eve.paid_out_at
             ,stg_eve.charged_back_at
             ,stg_eve.submitted_at
             ,stg_eve.failed_at
             ,stg_eve.pending_submission_at
         from int_payment_milestones stg_eve
        left join dim_dates as conf_dt
          on (date(stg_eve.confirmed_at) = conf_dt.calendar_date)
        left join dim_dates as failed_dt
          on (date(stg_eve.failed_at) = failed_dt.calendar_date)
        left join dim_dates as paid_out_dt
          on (date(stg_eve.paid_out_at) = paid_out_dt.calendar_date)  
        left join dim_dates as submitted_dt
          on (date(stg_eve.submitted_at) = submitted_dt.calendar_date)
        left join dim_dates as charged_back_dt
          on (date(stg_eve.charged_back_at) = charged_back_dt.calendar_date)
        left join dim_dates as pending_submission_dt
          on (date(stg_eve.pending_submission_at) = pending_submission_dt.calendar_date)    
      ) stg_dim_dates
        on (stg_dim_dates.payment_id = stg_pay.payment_id)
)

select * from final