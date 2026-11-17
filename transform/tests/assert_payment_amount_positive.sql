select payment_id
      ,amount
  from {{ref('stg_payments')}}
where amount<=0 