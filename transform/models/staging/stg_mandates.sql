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
        date(created_at) as created_at,
        date(cancelled_at) as cancelled_at
    from source
)

select * from renamed