with customers as (

    select * from {{ ref('stg_customers') }}

),

countries as (
    select * from {{ref('countries')}}
),

final as (

    select
        {{ dbt_utils.generate_surrogate_key(['cust.customer_id']) }} as customer_sk,
        cust.customer_id,
        cust.name, 
        cust.email, 
        cust.country,
        cust.created_at,
        ctr.country_name
    from customers cust
    left join countries ctr
      on cust.country = ctr.country_code
)

select * from final