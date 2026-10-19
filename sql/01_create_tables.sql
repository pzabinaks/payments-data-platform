DROP TABLE IF EXISTS payments;
create table payments (payment_id varchar(100) not null, 
                       customer_id varchar(50), 
                       merchant varchar(200),
                       amount numeric(12, 2) not null CHECK (amount > 0),
                       currency varchar(3) not null CHECK (currency IN ('EUR', 'GBP')),
                       status varchar(100) not null CHECK (status IN ('paid', 'failed', 'pending', 'cancelled')),
                       created_at timestamp,
                       PRIMARY KEY (payment_id)
                     );

DROP TABLE IF EXISTS fx_rates;
create table fx_rates (rate_date date not null,
                       base varchar(3) not null,
                       quote varchar(3) not null,
                       rate DECIMAL(12, 6) not null CHECK (rate > 0),
                       PRIMARY KEY (rate_date,base,quote,rate)
                     );                     