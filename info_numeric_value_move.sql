/*
SQL to move numeric INFO key val rows to another table where the values are stored as REAL
The identification of rows with INFO numeric values is two-step:
1. Identify and copy zeroes
2. Identify and copy non-zero numbers by exploiting SQLite's coercion of text values 
     when multiplied by one. Non-numeric text returns 0 while numbers return the numeric value
*/
-- Identify and copy zeroes ('0' or '0.0' formats) in INFO values
-- The nested REPLACEs and TRIM can be used to identify and filter values that contain only decimal oint (.)
--  and 0
INSERT INTO info_key_num_val(variant_id, info_key, info_num_val)
SELECT
  variant_id,
  info_key, 
  info_str_val
FROM
  info_key_str_val
WHERE
  LENGTH(REPLACE(REPLACE(TRIM(info_str_val), '0', ''), '.', '')) = 0;

-- Numeric non-zero numbers can be identified by multiplying them by one.
-- Text values that contain characters other than digits and decimal points
--  return 0 when multiplied by 1 so any non-zero returned must be a non-zero number.
INSERT INTO info_key_num_val(variant_id, info_key, info_num_val)
SELECT
  variant_id,
  info_key, 
  info_str_val
FROM
  info_key_str_val
WHERE
  info_str_val * 1 <> 0;

-- Remove all rows identified in the earlier queries as being numeric
DELETE 
FROM 
  info_key_str_val     
WHERE EXISTS (SELECT *
              FROM
                info_key_num_val
              WHERE
                info_key_num_val.variant_id = info_key_str_val.variant_id);