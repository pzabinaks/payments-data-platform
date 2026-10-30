-- Simulated source extract as of 2026-07-01
DROP TABLE IF EXISTS stg_merchants_2026_07;
CREATE TABLE stg_merchants_2026_07 AS SELECT * FROM stg_merchants;

-- Type 2 change: 20 merchants change category
UPDATE stg_merchants_2026_07
SET category = CASE category
    WHEN 'gym' THEN 'media'      WHEN 'saas' THEN 'telecom'
    WHEN 'utilities' THEN 'insurance' WHEN 'insurance' THEN 'utilities'
    WHEN 'media' THEN 'gym'      WHEN 'telecom' THEN 'saas' END
WHERE merchant_id BETWEEN 'MER00001' AND 'MER00020';

-- Type 2 change: 5 merchants move country
UPDATE stg_merchants_2026_07
SET country = CASE WHEN country = 'FR' THEN 'DE' ELSE 'FR' END
WHERE merchant_id BETWEEN 'MER00021' AND 'MER00025';

-- Type 1 change: 5 name corrections
UPDATE stg_merchants_2026_07
SET name = upper(name)
WHERE merchant_id BETWEEN 'MER00026' AND 'MER00030';

-- 3 new merchants
INSERT INTO stg_merchants_2026_07 (merchant_id, name, category, country) VALUES
  ('MER00501', 'Baltic Fitness SIA', 'gym',  'LV'),
  ('MER00502', 'Nordlicht Media GmbH', 'media', 'DE'),
  ('MER00503', 'Thames Telecom Ltd', 'telecom', 'GB');