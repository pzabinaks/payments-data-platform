with source as (
    select * from {{ source('raw', 'mandates') }}
),

renamed as (
    select
        mandate_id,
        customer_id,	
        merchant_id,
        scheme,
        currency,
        status,
        created_at,
        cancelled_at
    from source
)

select * from renamed