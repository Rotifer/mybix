/*
Populate the info_keynum_val and info_key_str_val tables with
the appropriate data from the load table info_key_val.
Once done drop the load table
*/

INSERT INTO info_key_num_val(variant_id, info_key, info_num_val)
SELECT
  variant_id,
  info_key, 
  info_val
FROM
  info_key_val
WHERE
  datatype = 'num';

INSERT INTO info_key_str_val(variant_id, info_key, info_str_val)
SELECT
  variant_id,
  info_key, 
  info_val
FROM
  info_key_val
WHERE
  datatype = 'str';
