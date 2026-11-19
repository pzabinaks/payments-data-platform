with final as (

    select
     cast(format_date('%Y%m%d', d) as int64) as date_sk
    ,d as calendar_date
    ,extract(month from d) as month
    ,extract(year from d) as year
    ,extract(quarter from d) as quarter
    ,mod(extract(dayofweek from d) + 5, 7) + 1 as day_in_week -- Monday day 1
    ,case when mod(extract(dayofweek from d) + 5, 7) + 1 >= 6 then 1 else 0 end as weekend_day
    ,format_date('%B', d) as month_name
    ,cast(format_date('%Y%m', d) as int64) as year_month
from unnest(generate_date_array('2024-12-01', '2026-12-31')) as d

)

select * from final