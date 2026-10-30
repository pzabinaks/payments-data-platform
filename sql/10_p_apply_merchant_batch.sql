--apply_merchant_batch(p_src regclass, p_batch_date date)
CREATE OR REPLACE PROCEDURE p_apply_merchant_batch(
    p_src regclass,
    p_batch_date date
) 
LANGUAGE plpgsql AS $$
declare
  v_sql text;
BEGIN
    --1 handle Type1: name
execute format(
    $query$
    UPDATE dim_merchant_scd2 as dim_mer2
         set name = stg.name
       from (
              select stg_mer.name, stg_mer.merchant_id
              from dim_merchant_scd2 dim_mer
              join %s stg_mer
                on dim_mer.merchant_id = stg_mer.merchant_id
             WHERE dim_mer.is_current = true 
               AND dim_mer.name IS DISTINCT FROM stg_mer.name
            ) stg
        where stg.merchant_id = dim_mer2.merchant_id
        $query$,
       p_src
    );


   --2 handle Type2: country and category
    EXECUTE format(    
    $query$
    with updated_merchants(merchant_id) 
     as ( UPDATE dim_merchant_scd2 as dim_mer2
             set is_current = false
                ,valid_to = $1
           from  (select stg_mer.country,dim_mer.country as dim_country,stg_mer.name,dim_mer.category as dim_category,stg_mer.merchant_id
                                  from dim_merchant_scd2 dim_mer
                                  join %s stg_mer
                                    on dim_mer.merchant_id = stg_mer.merchant_id
                                 WHERE is_current=true 
                                   AND (dim_mer.country IS DISTINCT FROM stg_mer.country or dim_mer.category IS DISTINCT FROM stg_mer.category)
                                ) stg
            where stg.merchant_id = dim_mer2.merchant_id and dim_mer2.is_current = true
        RETURNING dim_mer2.merchant_id
        )
 insert into dim_merchant_scd2 
        (merchant_id
        ,name
        ,category
        ,country
        ,valid_from 
        ,valid_to 
        ,is_current
        )     
  select stg_mer2.merchant_id
        ,stg_mer2.NAME
        ,stg_mer2.category
        ,stg_mer2.country  
        ,$1
        ,$2
        ,True
    from %s stg_mer2
    join updated_merchants u_mer
     on (u_mer.merchant_id = stg_mer2.merchant_id)
    $query$ 
    ,p_src
    ,p_src
    ) USING p_batch_date,to_date('9999-12-31','YYYY-MM-DD');


   
    --3 Add new merchants from batch
    EXECUTE format( 
      $query$
      insert into dim_merchant_scd2 
        (merchant_id
        ,name
        ,category
        ,country
        ,valid_from 
        ,valid_to 
        ,is_current
        )
select stg_mer2.merchant_id
        ,stg_mer2.NAME
        ,stg_mer2.category
        ,stg_mer2.country  
        ,$1
        ,$2
        ,True
    from %I stg_mer2
 where not exists (select 1 from dim_merchant_scd2 dim_mer2 where dim_mer2.merchant_id = stg_mer2.merchant_id)
 $query$
 ,p_src
    )
   USING p_batch_date,to_date('9999-12-31','YYYY-MM-DD');
    --RAISE NOTICE 'SQL: %', v_sql;  
    --EXECUTE v_sql;

END;
$$;