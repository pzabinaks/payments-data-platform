select
    round(safe_divide(sum(cast(is_failed as int64)), count(*)), 3) as failure_rate,
    dim_mer.category,
    dim_dat.year,
    dim_dat.month
from {{ ref('fct_payments') }} as fct_pay
join {{ ref('dim_merchants') }} as dim_mer
    on fct_pay.merchant_sk = dim_mer.merchant_sk
join {{ ref('dim_dates') }} as dim_dat
    on fct_pay.charge_date_sk = dim_dat.date_sk
group by
    dim_mer.category,
    dim_dat.year,
    dim_dat.month
order by
    failure_rate desc