with source as (
    select * from {{ source('raw', 'payments') }}
),

renamed as (
    select
        payment_id,
        mandate_id,
        cast(amount as numeric) amount,
        currency,
        date(charge_date) as charge_date,
        status,	
        failure_reason
    from source
)

select * from renamed