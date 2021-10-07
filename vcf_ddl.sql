CREATE TABLE info_key_val(
  variant_id TEXT,
  info_key TEXT,
  info_val TEXT
);
CREATE TABLE info_flag(
  variant_id TEXT,
  info_flag TEXT
);
CREATE TABLE variant_detail(
  chromosome TEXT,
  position INT,
  variant_id TEXT,
  ref_allele TEXT,
  alt_allele TEXT
);