-- DIM_DATE ---------------------------------------------------------------
-- dim_date (date_sk integer     -- surrogate key / format YYYYMMDD
--              ,date  DATE  -- real
--              ,month  integer      -- month of the year
--              ,year   integer      -- year
--              ,quarter integer     -- quarter of the year
--              ,day_in_week integer -- day ina week
--              ,weekend_day   integer   -- flag: 0- false 1- true
--              );

DROP TABLE IF EXISTS dim_date;

create table dim_date (
              date_sk integer     -- surrogate key / format YYYYMMDD
             ,date  DATE  -- real
             ,month  integer      -- month of the year
             ,year   integer      -- year
             ,quarter integer     -- quarter of the year
             ,day_in_week integer -- day ina week
             ,weekend_day   integer   -- flag: 0- false 1- true
             ,month_name varchar   --name of the month
             ,year_month varchar   -- year and month in format YYYY-MM
             ,PRIMARY KEY(date_sk)
             );

insert into dim_date
SELECT  to_char(n.n2, 'YYYYMMDD')::integer
      , n as date
      , extract(month from n) as "month"
      , extract(year from n) as "year"
      , extract(quarter from n) as "quarter"
      , extract(isodow from n) as "day_in_week"
      , case when extract(isodow from n) >= 6 then 1 else 0 end as weekend_day
      , to_char(n, 'Mon') as month_name
      , to_char(n, 'YYYY-MM') as year_month
FROM (select a::date n ,a as n2 from generate_series('2024-12-01'::date, '2026-12-31'::date, interval '1 day') a) n;