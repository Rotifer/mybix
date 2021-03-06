CREATE UNIQUE INDEX var_id_detail_uniq_idx ON variant_detail(variant_id);
CREATE INDEX chr_pos_detail_idx ON variant_detail(chromosome, position);
CREATE UNIQUE INDEX var_flag_uniq_idx  ON info_flag(variant_id, info_flag);
CREATE UNIQUE INDEX var_key_str_uniq_idx  ON info_key_str_val(variant_id, info_key);
CREATE UNIQUE INDEX var_key_num_uniq_idx  ON info_key_num_val(variant_id, info_key);