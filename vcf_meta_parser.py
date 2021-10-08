import os
import re

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
        self.info_properties = ['ID', 'Number', 'Type', 'Description']
        self.metadata_lines = self.get_metadata_lines()

    def get_metadata_lines(self):
        """Return a list of metadata lines, that is, those beginning with ##, in the VCF file"""
        metadata_lines = []
        with open(self.vcf_file_path, 'rt') as fh:
            for line in fh:
                if line.startswith('#CHROM'):
                    break
                elif line.startswith('##'):
                    metadata_lines.append(line.strip(os.linesep))
            return metadata_lines

    def create_info_maps(self):
        """Extract INFO metadata from the metadata lines and return them as a list of dictionaries"""
        info_maps = []
        info_lines = [md_line for md_line in self.metadata_lines 
                        if md_line.startswith('##INFO=')]
        for info_line in info_lines:
            info_map = {}
            for info_property in self.info_properties:
                re_pat = '{}=([^,>"]*)'.format(info_property)
                match = re.search(re_pat, info_line)
                if match:
                    info_val = match.group(1)
                    info_map[info_property] = info_val
            info_maps.append(info_map)
        return info_maps

    def convert_info_maps_to_table(self):
        """"""
        info_maps = self.create_info_maps()
        info_table_column = {}
        for info_property in self.info_properties:
            info_table_column[info_property] = []
            for info_map in info_maps:
                info_table_column[info_property].append(info_map[info_property])
        return info_table_column

if __name__ == '__main__':
    from pprint import pprint
    dir_path = '{}/big_files/'.format(os.environ['HOME']) 
    vcf_file_path = os.path.join(dir_path, 'UKB_WGS_graphtyper_SVs_150k_sites.vcf')
    vcf_meta_parser = VCFMetaParser(vcf_file_path, dir_path)
    #pprint(vcf_meta_parser.get_metadata_lines())
    info_table = vcf_meta_parser.convert_info_maps_to_table()
    pprint(info_table)