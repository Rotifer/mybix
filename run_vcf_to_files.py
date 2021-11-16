from vcf_to_files import VCFToFiles
import sys
vcf_file_path = sys.argv[1]
dir_path = sys.argv[2]
vcf2files = VCFToFiles(vcf_file_path, dir_path)
vcf2files.write_variant_rows_to_files()  