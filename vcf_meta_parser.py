import os

class VCFMetaParser:
    """
    Parse the VCF metadata from VCF files
    The metadata is contained in lines beginning ## at the top of the VCF file
    The aim is to generate a tabular representation of the data
    """
    def __init__(self, vcf_file_path, output_dir):
        """"""
        self.vcf_file_path = vcf_file_path
        self.output_dir = output_dir
        self.metadata_lines = self.get_metadata_lines()

    def get_metadata_lines(self):
        """Return a list of metadata lines in the VCF file"""
        metadata_lines = []
        with open(self.vcf_file_path, 'rt') as fh:
            for line in fh:
                if line.startswith('#CHROM'):
                    break
                elif line.startswith('##'):
                    metadata_lines.append(line.strip(os.linesep))
            return metadata_lines

if __name__ == '__main__':
    from pprint import pprint
    dir_path = '{}/big_files/'.format(os.environ['HOME']) 
    vcf_file_path = os.path.join(dir_path, '1000GENOMES-phase_3.vcf')
    vcf_meta_parser = VCFMetaParser(vcf_file_path, dir_path)
    pprint(vcf_meta_parser.get_metadata_lines())