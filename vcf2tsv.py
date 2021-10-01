import os
import sys
import csv

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
        with open(self.vcf_file_path) as fh:
            csv_reader = csv.reader(fh, delimiter='\t', quotechar='"')
            for row in csv_reader:
                if row_start:
                    columns_keep =[row[i] for i in column_indexes_to_keep]
                    fho.write(('\t').join(columns_keep) + os.linesep)
                if row[0].startswith('#CHROM'):
                    row_start = True
        fho.close() 

if __name__ == '__main__':
    dir_path = '{}/big_files/'.format(os.environ['HOME']) 
    vcf_file_path = os.path.join(dir_path, '1000GENOMES-phase_3_1k_sample.vcf')
    header_file_path = os.path.join(dir_path, 'vcf_header.txt')
    body_file_path = os.path.join(dir_path, 'vcf_body.tsv') 
    vcf2tsv = VCF2TSV(vcf_file_path)
    vcf2tsv.write_header_to_file(header_file_path)
    vcf2tsv.write_body_to_file(body_file_path)