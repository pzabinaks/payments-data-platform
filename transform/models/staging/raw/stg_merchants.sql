with source as (
    select * from {{ source('raw', 'merchants') }}
),

renamed as (
    select
        merchant_id,
        name,	
        category,	
        country
    from source
)

select * from renamed