import os
import sys
import csv
import re

class VCF2TSV:
    """
    """
    def __init__(self, vcf_file_path):
        """
        """
        self.vcf_file_path = vcf_file_path
        if not os.path.exists(self.vcf_file_path):
            raise IOError('Given file "{}" does not exist!'.format(self.vcf_file_path))
    
    def write_header_to_file(self, output_file):
        """

        """
        fho = open(output_file, 'wt')
        with open(self.vcf_file_path) as fh:
            for row in fh:
                if row.startswith('#CHROM'): break
                fho.write(row)
        fho.close()

    def write_body_to_file(self, output_file):
        """

        """
        column_names = ['chrom', 'pos', 'id', 'ref', 'alt', 'info']
        column_indexes_to_keep = [0, 1, 2, 3, 4, 7]
        row_start = False
        fho = open(output_file, 'wt')
        fho.write('\t'.join(column_names) + os.linesep)
        with open(self.vcf_file_path) as fh:
            csv_reader = csv.reader(fh, delimiter='\t', quotechar='"')
            for row in csv_reader:
                if row_start:
                    columns_keep =[row[i] for i in column_indexes_to_keep]
                    fho.write(('\t').join(columns_keep) + os.linesep)
                if row[0].startswith('#CHROM'):
                    row_start = True
        fho.close() 

    def get_info_rows(self):
        """
        """
        info_rows = []
        with open(self.vcf_file_path) as fh:
            for row in fh:
                if row.startswith('#CHROM'): break
                if row.startswith('##INFO'):
                    info_rows.append(row)
        return info_rows

    def generate_info_schema(self):
        info_rows = self.get_info_rows()
        regex_pat = r'[<](.+),Description="'
        info_schema = {}
        for info_row in info_rows:
            match = re.search(regex_pat, info_row)
            if match:
                matched_info = match.group(1)
                info_schema_element = dict(entry.split("=") for entry in matched_info.split(','))
                element_id = info_schema_element['ID']
                info_schema_element.pop('ID') 
                info_schema[element_id] = info_schema_element
        return info_schema

if __name__ == '__main__':
    from pprint import pprint
    dir_path = '{}/big_files/'.format(os.environ['HOME']) 
    vcf_file_path = os.path.join(dir_path, '1000GENOMES-phase_3_1k_sample.vcf')
    header_file_path = os.path.join(dir_path, 'vcf_header.txt')
    body_file_path = os.path.join(dir_path, 'vcf_body.tsv') 
    vcf2tsv = VCF2TSV(vcf_file_path)
    #vcf2tsv.write_header_to_file(header_file_path)
    #vcf2tsv.write_body_to_file(body_file_path)
    pprint(vcf2tsv.generate_info_schema())