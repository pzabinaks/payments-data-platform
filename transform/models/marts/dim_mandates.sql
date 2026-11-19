with mandates as (

    select * from {{ ref('stg_mandates') }}

),


final as (

    select
        {{ dbt_utils.generate_surrogate_key(['man.mandate_id']) }} as mandate_sk,
        mandate_id,
        customer_id,	
        merchant_id,
        scheme,
        currency,
        status,
        created_at,
        cancelled_at,
        case when status='active' then 1 else 0 end as is_active
    from mandates man
)

select * from final