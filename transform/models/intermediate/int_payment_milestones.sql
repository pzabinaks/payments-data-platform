with events as (

    select * from {{ ref('stg_events') }}

),

final as (

    select payment_id
          ,max(case when status = 'submitted' then event_at end) as submitted_at
          ,max(case when status = 'paid_out' then event_at end) as paid_out_at          
          ,max(case when status = 'failed' then event_at end) as failed_at
          ,max(case when status = 'charged_back' then event_at end) as charged_back_at        
          ,max(case when status = 'pending_submission' then event_at end) as pending_submission_at
          ,max(case when status = 'confirmed' then event_at end) as confirmed_at       
      from events
     group by payment_id 
)

select * from final

