create table payments (payment_id varchar(100) not null, 
                       customer varchar(50), 
                       merchant varchar(200),
                       amount numeric,
                       currency varchar(3) ,
                       "status" varchar(50),
                       created_at datetime,
                       PRIMARY KEY (articlpayment_id)
                     );

create table fx_rates (rate_date datetime not null,
                       base varchar(3) not null,
                       quote varchar(3) not null,
                       rate DECIMAL(19, 4) not null,
                       PRIMARY KEY (articlpayment_id)
                     );                     