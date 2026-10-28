--# DIM_CUSTOMER -------------------------------------------------------------------------------------

DROP TABLE IF EXISTS dim_customer;


CREATE TABLE dim_customer (customer_sk integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- surrogate key: 1, 2, 3, ...
 customer_id text NOT NULL UNIQUE, -- natural key from the source
 name text, -- PII
 email text, -- PII
 country text NOT NULL,
              created_at timestamp NOT NULL);


INSERT INTO dim_customer (customer_id, name, email, country, created_at)
SELECT customer_id,
       name,
       email,
       country,
       created_at
FROM stg_customers
ORDER BY customer_id;

--# DIM_MERCHANT   -------------------------------------------------------------------------------------

DROP TABLE IF EXISTS dim_merchant;


CREATE TABLE dim_merchant(merchant_sk integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY --surrogate key 1,2,3
 ,merchant_id text NOT NULL UNIQUE -- id from merchans
 ,name text -- name
 ,category text -- category
 ,country text NOT NULL -- country
);


INSERT INTO dim_merchant (merchant_id, name, category, country)
select merchant_id,
       name,
       category,
       country
from stg_merchants
ORDER BY merchant_id;

--# DIM_MANDATE    -------------------------------------------------------------------------------------

DROP TABLE IF EXISTS dim_mandate;


CREATE TABLE dim_mandate(mandate_sk integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ,mandate_id text NOT NULL UNIQUE
  ,scheme text ,currency text NOT NULL
  ,status text NOT NULL
  ,created_at date 
  ,cancelled_at date
);


insert into dim_mandate(mandate_id, scheme, currency, status, created_at, cancelled_at)
select mandate_id,
       scheme,
       currency,
       status,
       created_at::date,
       cancelled_at::date
from stg_mandates
order by mandate_id;