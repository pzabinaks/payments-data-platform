{{ config(
    materialized = 'incremental',
    unique_key = 'event_id',
    partition_by = {'field': 'event_at', 'data_type': 'timestamp', 'granularity': 'month'},
    incremental_predicates = [
  "DBT_INTERNAL_DEST.event_at > timestamp('2026-09-01')"
]
) }}
--fixed date because the test data ends 2026-10-15; in production use current_timestamp() minus a window wider than the lookback

select {{ dbt_utils.generate_surrogate_key(['stg_eve.event_id']) }} as event_sk
      ,stg_eve.event_id
      ,fct_pay.payment_id
      ,fct_pay.payment_sk
      ,cast(format_date('%Y%m%d', date(event_at)) as int64) date_sk
      ,stg_eve.event_at
      ,stg_eve.status
      ,fct_pay.customer_sk
      ,fct_pay.merchant_sk
      ,fct_pay.mandate_sk
from {{ ref('stg_events') }} stg_eve
join {{ ref('fct_payments')}} fct_pay
  on stg_eve.payment_id=fct_pay.payment_id


{% if is_incremental() %}
  -- only on incremental runs: rows newer than what's already in the table
  where event_at > (select timestamp_sub(max(event_at), interval 20 day) from {{ this }})
{% endif %}