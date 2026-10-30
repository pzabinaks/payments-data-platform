begin;
  CALL p_apply_merchant_batch('stg_merchants_2026_07', to_date('2026-07-01','YYYY-MM-DD')); --check data after this step
  CALL p_apply_merchant_batch('stg_merchants_2026_10', to_date('2026-10-01','YYYY-MM-DD'));
-- rollback; if needed
commit; 


select *
from stg_merchants_2026_07
where merchant_id='MER00001';

select *
from stg_merchants_2026_10
where merchant_id='MER00001';

------------------------------------------------------------------------------------------------
--task #4 -- payment counts by modified categories
select count(1) as payment_count,dim_mer2.merchant_id,dim_mer2.category
  from stg_payments stg_pay
  join stg_mandates stg_man 
    on stg_pay.mandate_id = stg_man.mandate_id
  join dim_merchant_scd2 dim_mer2
    on stg_man.merchant_id = dim_mer2.merchant_id 
    and stg_pay.charge_date::date>= dim_mer2.valid_from AND stg_pay.charge_date::date < dim_mer2.valid_to
    --and (stg_pay.charge_date::date between dim_mer2.valid_from and dim_mer2.valid_to)
  where stg_man.merchant_id between 'MER00001'and 'MER00020'
  group by dim_mer2.merchant_id,dim_mer2.category
  order by 2,3;

--tast #5
-- 1. exactly one current row per merchant                → 0 rows
SELECT merchant_id FROM dim_merchant_scd2 WHERE is_current GROUP BY merchant_id HAVING COUNT(*) <> 1;
-- 2. counts                                               → 528 total, 503 current, 25 closed
SELECT COUNT(*), COUNT(*) FILTER (WHERE is_current), COUNT(*) FILTER (WHERE NOT is_current) FROM dim_merchant_scd2;
-- 3. idempotency: run Task 3 a second time                 → counts must not change
--528	503	25

--task #6
WITH date_checks AS (
    SELECT 
        merchant_id,
        valid_from,
        valid_to,
        -- Fetch the next row's starting date
        LEAD(valid_from) OVER (
            PARTITION BY merchant_id 
            ORDER BY valid_from
        ) AS next_valid_from
    FROM dim_merchant_scd2
)
SELECT 
    merchant_id,
    valid_from,
    valid_to,
    next_valid_from,
    CASE 
        WHEN valid_to < next_valid_from THEN 'Gap'
        WHEN valid_to > next_valid_from THEN 'Overlap'
    END AS issue_type
FROM date_checks
-- Filter for rows where valid_to doesn't cleanly transition to the next valid_from
WHERE (valid_to < next_valid_from or valid_to > next_valid_from);

---chek names--------------------------------------------------------------------------------------------
SELECT d.merchant_id, d.name, s.name FROM dim_merchant_scd2 d
JOIN stg_merchants_2026_07 s USING (merchant_id) WHERE d.name IS DISTINCT FROM s.name;