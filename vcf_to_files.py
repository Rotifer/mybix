import os
import csv
"""
Decompose a VCF file to a set of files for database upload.
"""

class VCFToFiles:
    def __init__(self, vcf_file_path, output_dir, column_separator='\t'):
        """Instantiate with a path to a readable VCF file"""
        self.vcf_file_path = vcf_file_path
        self.output_dir = output_dir
        self.column_separator = column_separator
        assert os.path.isfile(vcf_file_path) and os.access(vcf_file_path, os.R_OK), \
            "File {} doesn't exist or isn't readable".format(vcf_file_path)
        #self.vcf_dirname = os.path.dirname(vcf_file_path)
        self.vcf_basename = os.path.basename(vcf_file_path)
        self.vcf_name_minus_ext = os.path.splitext(self.vcf_basename)[0]
        #self.output_file_type_name_map = {"header": os.path.join(self.vcf_dirname, )}

    def write_header_file(self):
        """Write the header lines, that is, those beginning with ## to a given output file.
        TODO: May need more processing.
        """
        output_file = os.path.join(self.output_dir, self.vcf_name_minus_ext + '_header.txt')
        fho = open(output_file, 'wt')
        with open(self.vcf_file_path) as fh:
            for row in fh:
                if row.startswith('#CHROM'): break
                fho.write(row)
        fho.close()

    def _make_output_file_names_map(self):
        """"""
        name_base = os.path.join(self.output_dir, self.vcf_name_minus_ext)
        output_file_names_map = {
            'header': name_base + '_header.txt',
            'variant_details': name_base + '_variant_details.txt',
            'info_keys_vals': name_base + '_info_keys_vals.txt',
            'info_flags': name_base + '_info_flags.txt',
            'variant_qual_filter': name_base + '_variant_qual_filter.txt'}
        return output_file_names_map

    def _make_variant_details(self, row):
        """"""
        columns_to_keep = [0, 1, 2, 3, 4]
        variant_detail_row = [row[i] for i in columns_to_keep]
        return self.column_separator.join(variant_detail_row) + os.linesep

    def _make_info_keys_vals(self, row):
        """"""
        info_column_index = 7
        variant_id_index = 2
        variant_id, info_value = row[variant_id_index], row[info_column_index]
        info_pairs = [info_pair.replace('=', self.column_separator)
                        for info_pair in info_value.split(';') 
                            if '=' in info_pair]
        info_out_values = [self.column_separator.join([variant_id, info_pair])
                            for info_pair in info_pairs]
        return os.linesep.join(info_out_values) + os.linesep

    def _make_info_flags(self, row):
        """"""
        info_column_index = 7
        variant_id_index = 2
        variant_id, info_value = row[variant_id_index], row[info_column_index]
        info_flags = [self.column_separator.join([variant_id, info_flag]) 
                        for info_flag in info_value.split(';')
                            if '=' not in info_flag and info_flag != '']
        return os.linesep.join(info_flags) + os.linesep

    def write_variant_rows_to_files(self):
        """"""
        output_file_names_map = self._make_output_file_names_map()
        fh_vd = open(output_file_names_map['variant_details'], 'wt')
        fh_vd.write(self.column_separator.join(['chromosome', 'position', 'variant_id', 'ref_allele', 'alt_allele']) + os.linesep)
        fh_ikv = open(output_file_names_map['info_keys_vals'], 'wt')
        fh_ikv.write(self.column_separator.join(['variant_id', 'info_key', 'info_val']) + os.linesep)
        fh_if = open(output_file_names_map['info_flags'], 'wt')
        fh_if.write(self.column_separator.join(['variant_id', 'info_flag']) + os.linesep)
        row_start = False
        with open(self.vcf_file_path) as fh:
            csv_reader = csv.reader(fh, delimiter='\t')
            for row in csv_reader:
                if row_start:
                    vd_row = self._make_variant_details(row)
                    fh_vd.write(vd_row)
                    ikv_rows = self._make_info_keys_vals(row)
                    fh_ikv.write(ikv_rows)
                    if_row = self._make_info_flags(row)
                    fh_if.write(if_row)
                if row[0].startswith('#CHROM'):
                    row_start = True
        fh_vd.close()
        fh_ikv.close()
        fh_if.close()

if __name__ == '__main__':
    from pprint import pprint
    dir_path = '{}/big_files/'.format(os.environ['HOME']) 
    vcf_file_path = os.path.join(dir_path, '1000GENOMES-phase_3_1k_sample.vcf')
    vcf2files = VCFToFiles(vcf_file_path, dir_path)
    vcf2files.write_variant_rows_to_files()