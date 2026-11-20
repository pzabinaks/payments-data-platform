select
    fct_payment_eve_cnt,
    stg_eve_cnt
from (
    select
        (select count(1) from {{ ref('fct_payment_events') }}) as fct_payment_eve_cnt,
        (select count(1) from {{ ref('stg_events') }}) as stg_eve_cnt
) a
where a.stg_eve_cnt <> a.fct_payment_eve_cnt