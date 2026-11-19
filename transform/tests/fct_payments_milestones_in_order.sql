select payment_id
from {{ref('fct_payments')}} pmt
join {{ref('dim_dates')}} paid_out
  on pmt.paid_out_date_sk=paid_out.date_sk
join {{ref('dim_dates')}} submitted_at
  on pmt.submitted_date_sk=submitted_at.date_sk  
where paid_out.calendar_date < submitted_at.calendar_date