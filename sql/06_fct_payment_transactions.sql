--# fct_payment_transactions    -------------------------------------------------------------------------------------

DROP TABLE IF EXISTS fct_payment_transactions;


CREATE TABLE fct_payment_transactions (paym_trx_sk bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY    
                                      ,event_id text NOT NULL UNIQUE   -- id from payemnt_events
                                      ,payment_id_sk  bigint           --FK to payments
                                      ,transaction_date_sk  integer    --FK to dim_date
                                      ,status varchar NOT NULL         -- Degenerate Dimension status
                                      ,customer_sk  integer            -- FK to dim_customer
                                      ,merchant_sk  integer            -- FK to dim_merchant
                                      ,mandate_sk   integer            -- FK to mandate
                                     );



insert into fct_payment_transactions (event_id
                                      ,payment_id_sk
                                      ,transaction_date_sk
                                      ,status
                                      ,customer_sk
                                      ,merchant_sk
                                      ,mandate_sk
                                     )
SELECT event_id
      ,fct_pay.payment_id_sk
      ,dim_dat.date_sk
      ,stg_eve.status
      ,customer_sk
      ,merchant_sk
      ,mandate_sk
from stg_events stg_eve
left join fct_payments fct_pay
  on (stg_eve.payment_id = fct_pay.payment_id)
left join dim_date dim_dat
   on (stg_eve.event_at::date = dim_dat.calendar_date);