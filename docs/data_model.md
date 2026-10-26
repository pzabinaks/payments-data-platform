Business process: payment handling

Fact tables:
    First fact table would be payemnts itself, second payment_events(transacitons?)

        fct_payments(pament_id_sk BIGINT  -- surrogate key for payment
                    ,payment_id VARCHAR2  --payment_id from payements
                    ,charge_date_sk INT   -- FK to dim_date
                    ,customer_sk  INT     -- FK to dim_customer
                    ,merchamt_sk  INT     -- FK to dim_merchant
                    ,amount       number  -- amount (measure)
                    ,customer_sk  INT
                    )

        fct_payment_transactions (paym_trx_sk BIGINT --rurrogate key for payment_events/transacions 
                                 ,event_id varchar2 -- id from payemnt_events
                                 ,event_at_sk      --FK to dim_date
                                 ,status varchar   -- Degenerate Dimension status
                                  );
Dimetions:
    dim_date (date_sk INT     -- surrogate key / format DDMMYYYY
             ,date  DATETIME  -- real datetime
             ,month  INT      -- month of the year
             ,year   INT      -- year
             ,quarter INT     -- quarter of the year
             ,day_in_week INT -- day ina week
             ,weekend_day   BOOL -- is it a weekend day
             );
    
    dim_customer (customer_sk INT       -- surrogate key 1,2,3...
                 ,customer_id VARCHAR2  -- id from customers
                 ,name        VARCHAR2  -- name
                 ,email       VARCHAR2  -- email   
                 ,country     VARCHAR2  -- country
                 );
              
    dim_merchant(merchamt_sk  INT        --surrogate key 1,2,3
                ,merchand_id varchar2   -- id from merchans
                 ,name        VARCHAR2  -- name
                 ,category    VARCHAR2  -- category   
                 ,country     VARCHAR2  -- country
                );
    
    

