# File for checking things and developing prototypes
import os
import sys
def parse_vcf_info(vcf_row):
    column_separator = '\t'
    row = vcf_row.split(column_separator)
    info_column_index = 7
    variant_id_index = 2
    variant_id, info_value = row[variant_id_index], row[info_column_index]
    info_pairs = [info_pair.split('=') for info_pair 
                    in info_value.split(';') 
                        if '=' in info_pair]
    info_lines = []
    for info_pair in info_pairs:
        info_line_elements = [variant_id, info_pair[0], info_pair[1]]
        if info_pair[1].replace('.', '').isdigit():
            info_line_elements.append('num')
        else:
           info_line_elements.append('str') 
        info_lines.append(column_separator.join(info_line_elements))
    return os.linesep.join(info_lines) + os.linesep

vcf_row = '1	10617	rs376342519	CGCCGTTGCAAAGGCGCGCCGC	C	.	.	dbSNP_154;TSA=indel;E_Freq;E_1000G;E_gnomAD;AFR=0.9894;AMR=0.9957;EAS=0.9911;EUR=0.994;SAS=0.9969'
print(parse_vcf_info(vcf_row))
print(sys.executable)