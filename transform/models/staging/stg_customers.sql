with source as (
    select * from {{ source('raw', 'customers') }}
),

renamed as (
    select
        customer_id,
        name, -- PII
        email, -- PII
        country,
        date(created_at) as created_at
    from source
)

select * from renamed