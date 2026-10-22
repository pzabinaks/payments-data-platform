select  sum (eur_amount)
from(
select p.payment_id, p.created_at, p.amount, r.rate_date, r.rate, round(p.amount / r.rate,2)  as eur_amount
from payments p
left join lateral 
  (select *
  from fx_rates r
   where  p.currency = r.quote and r.rate_date <= p.created_at::date
   ORDER BY r.rate_date DESC LIMIT 1
  )r ON true
where upper(p.currency) = 'GBP' and p.status='paid'
) a
--and date_trunc('day', p.created_at) = to_date('01.01.2026','DD.MM.YYYY')