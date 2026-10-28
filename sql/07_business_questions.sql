    -- 1 Failure rate by merchant category and month
    --     SUM(is_failed)::numeric / COUNT(*) GROUP BY dim_merchant.category, dim_date.year, dim_date.month

   select SUM(is_failed)  / COUNT(*) as failure_rate,dim_mer.category, dim_dat.year, dim_dat.month
   from fct_payments fct_pay
   join dim_merchant dim_mer
     on fct_pay.merchant_sk = dim_mer.merchant_sk
   join dim_date dim_dat
     on fct_pay.charge_date_sk = dim_dat.date_sk
    GROUP BY dim_mer.category, dim_dat.year, dim_dat.month
    order by 1 desc;
  

    -- 2 Total collected in EUR by scheme (SEPA vs Bacs) per quarter
    --     sum(fct_payments.amount_eur) GROUP BY dim_mandate.scheme, dim_date.year,dim_date.quarter

    -- 3 Average number of days from submission to payout, by scheme
    --     avg (fct_payments.days_to_payout) GROUP BY dim_mandate.scheme

    -- 4 Top failure reasons for customers in Germany
    --     where dim_customer.country = 'DE' group by fct_payments.failure_reason ORDER BY COUNT(*) DESC

    -- 5 How many payments were charged back, and how long after payout?
    --     fct_payments.days_to_charge_back where fct_payments.is_charged_back
