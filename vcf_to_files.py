import os
import csv
"""
Create a set of files from a VCF that can be loaded into a relational database
and that are designed to be optimally queryable with SQL.
TODO: 
- QUAL and FILTER not yet processed. Header rows need to be handled better.
- Separate class needed for the header
"""

class VCFToFiles:
    """Decompose a VCF file to a set of files for database upload.
    """
    def __init__(self, vcf_file_path, output_dir, column_separator='\t'):
        """Instantiate with a path to a readable VCF file, a directory path to where files
        are written and an optional column separator with tab as default."""
        self.vcf_file_path = vcf_file_path
        self.output_dir = output_dir
        self.column_separator = column_separator
        assert os.path.isfile(vcf_file_path) and os.access(vcf_file_path, os.R_OK), \
            "File {} doesn't exist or isn't readable".format(vcf_file_path)
        self.vcf_basename = os.path.basename(vcf_file_path)
        self.vcf_name_minus_ext = os.path.splitext(self.vcf_basename)[0]

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
        """Return a dictionary mapping shorthand keys to full paths
        for each of the generated oututput files.
        """
        name_base = os.path.join(self.output_dir, self.vcf_name_minus_ext)
        output_file_names_map = {
            'header': name_base + '_header.txt',
            'variant_details': name_base + '_variant_details.txt',
            'info_keys_vals': name_base + '_info_keys_vals.txt',
            'info_flags': name_base + '_info_flags.txt',
            'variant_qual_filter': name_base + '_variant_qual_filter.txt'}
        return output_file_names_map

    def _make_variant_details(self, row):
        """Given a VCF data row, return a string of column elements containing the chromosome,
        position, variant ID and ref and alt alleles with a new line appended."""
        columns_to_keep = [0, 1, 2, 3, 4]
        variant_detail_row = [row[i] for i in columns_to_keep]
        return self.column_separator.join(variant_detail_row) + os.linesep

    def _make_info_keys_vals(self, row):
        """Given a VCF data row, split on ';' and extract the INFO column and variant ID.
        Return a multi-line string containing three columns representing the variant ID
        and one column each for the INFO elements on each side of the = sign."""
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
            info_lines.append(self.column_separator.join(info_line_elements))
        return os.linesep.join(info_lines) + os.linesep
    
    def _make_info_flags(self, row):
        """Given a VCF data row, split on ';' and extract the INFO column and variant ID.
        Note: Some VCFs contain INFO elements with no flags, that is no ;FLAG; entries.
        If the INFO column contains flags:
            Return a multi-line string containing two columns, the variant ID and the INFO 
            flag values.
        Else: Return an empty string"""
        info_column_index = 7
        variant_id_index = 2
        variant_id, info_value = row[variant_id_index], row[info_column_index]
        info_flags = [info_flag for info_flag in info_value.split(';') 
                        if '=' not in info_flag and info_flag != '']
        if info_flags:
            info_flags_variants = [self.column_separator.join([variant_id, info_flag])
                                    for info_flag in info_flags]
            return os.linesep.join(info_flags_variants) + os.linesep
        return ''

    def write_variant_rows_to_files(self):
        """This is the method to be called by clients to generate the output files from the input VCF.
        Reads the VCF file and uses other methods to extract and format the information
        that it then writes to a set of files.
        TODO: Re-factor to remove the file opening and header line writing to a new method."""
        output_file_names_map = self._make_output_file_names_map()
        fh_vd = open(output_file_names_map['variant_details'], 'wt')
        fh_ikv = open(output_file_names_map['info_keys_vals'], 'wt')
        fh_if = open(output_file_names_map['info_flags'], 'wt')
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
                    # Do not print to the info flags file if there are no flags
                    if if_row:
                        fh_if.write(if_row)
                if row[0].startswith('#CHROM'):
                    row_start = True
        fh_vd.close()
        fh_ikv.close()
        fh_if.close()

if __name__ == '__main__':
    from pprint import pprint
    # Full 1000GENOMES-phase3.vcf takes 25-30 minutes
    dir_path = '{}/big_files/'.format(os.environ['HOME']) 
    vcf_file_path = os.path.join(dir_path, 'UKB_WGS_graphtyper_SVs_150k_sites.vcf')
    vcf2files = VCFToFiles(vcf_file_path, dir_path)
    vcf2files.write_variant_rows_to_files()