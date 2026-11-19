select
    fct_payment_cnt,
    stg_payment_cnt
from (
    select
        (select count(1) from {{ ref('fct_payments') }}) as fct_payment_cnt,
        (select count(1) from {{ ref('stg_payments') }}) as stg_payment_cnt
) a
where a.stg_payment_cnt <> a.fct_payment_cnt