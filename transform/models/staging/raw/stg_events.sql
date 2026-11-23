with source as (
    select * from {{ source('raw', 'events') }}
),

renamed as (
    select
        event_id,
        payment_id,
        status,
        event_at
    from source
)

select * from renamed