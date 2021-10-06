import os
"""
Decompose a VCF file to a set of files for database upload.
"""

class VCFToFiles:
    def __init__(self, vcf_file_path, output_dir):
        """Instantiate with a path to a readable VCF file"""
        self.vcf_file_path = vcf_file_path
        self.output_dir = output_dir
        assert os.path.isfile(vcf_file_path) and os.access(vcf_file_path, os.R_OK), \
            f"File {vcf_file_path} doesn't exist or isn't readable"
        #self.vcf_dirname = os.path.dirname(vcf_file_path)
        self.vcf_basename = os.path.basename(vcf_file_path)
        self.vcf_name_minus_ext = os.path.splitext(self.vcf_basename)[0]
        #self.output_file_type_name_map = {"header": os.path.join(self.vcf_dirname, )}

    def write_header_file(self):
        """Write the header lines, that is, those beginning with ## to a given output file
        """
        output_file = os.path.join(self.output_dir, self.vcf_name_minus_ext + '_header.txt')
        fho = open(output_file, 'wt')
        with open(self.vcf_file_path) as fh:
            for row in fh:
                if row.startswith('#CHROM'): break
                fho.write(row)
        fho.close()