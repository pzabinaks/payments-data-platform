with merchants as (

    select * from {{ ref('stg_merchants') }}

),

countries as (
    select * from {{ref('countries')}}
),

final as (

    select
        {{ dbt_utils.generate_surrogate_key(['mer.merchant_id']) }} as merchant_sk,
        merchant_id,
        name,	
        category,	
        country,
        country_name
    from merchants mer
    left join countries ctr
      on mer.country = ctr.country_code
)

select * from final