import os
import sys
import csv
import re
import json

"""
VCF (Variant Call Format) version 4.0 parser. Create TSV file versions for loading into
relational databases, DuckDB etc.
VCF (Variant Call Format) version 4.0 specification: https://www.internationalgenome.org/wiki/Analysis/vcf4.0/
"""

class VCF2TSV:
    """
    Create a tab-separated version of a Variant Call Format (VCF) file that can be uploaded 
    into a database.
    """
    def __init__(self, vcf_file_path):
        """
        Provide a full path to a readable standard VCF file.
        """
        self.vcf_file_path = vcf_file_path
        if not os.path.exists(self.vcf_file_path):
            raise IOError('Given file "{}" does not exist!'.format(self.vcf_file_path))
        self.info_schema = self.generate_info_schema()

    def write_header_to_file(self, output_file):
        """Write the header lines, that is, those beginning with ## to a given output file
        """
        fho = open(output_file, 'wt')
        with open(self.vcf_file_path) as fh:
            for row in fh:
                if row.startswith('#CHROM'): break
                fho.write(row)
        fho.close()

    def write_body_to_file(self, output_file):
        """Write that actual variant data rows to a TSV file.
        No processing is done on the INFO column in this method. 
        VCF QUAL and FILTER columns are dropped.
        """
        column_names = ['chrom', 'position', 'variant_id', 'ref_allele', 'alt_allele', 'info']
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
        """Return a list containing all the header rows beginning with ##.
        Returned list is the input for methods that extract the INFO IDs
        and their associated values.
        """
        info_rows = []
        with open(self.vcf_file_path) as fh:
            for row in fh:
                if row.startswith('#CHROM'): break
                if row.startswith('##INFO'):
                    info_rows.append(row)
        return info_rows

    def generate_info_schema(self):
        """Parse a list containing the indivual INFO entries to generate
        a dictionary of dictionaries mapping INFO ID to INFO details.
        """
        info_rows = self.get_info_rows()
        regex_pat = r'[<](.+),Description="'
        info_schema = {}
        column_index = 0 # Added to inner dicts to file set output column values for info entries
        for info_row in info_rows:
            match = re.search(regex_pat, info_row)
            if match:
                matched_info = match.group(1)
                info_schema_element = dict(entry.split("=") for entry in matched_info.split(','))
                element_id = info_schema_element['ID']
                info_schema_element.pop('ID') 
                info_schema_element['column_index'] = column_index
                column_index +=1
                info_schema[element_id] = info_schema_element
        return info_schema

    def get_info_column_names_in_order(self):
        """Return a list of the INFO IDs ordered by the column index value
        in the inner dictionaries. This list is used to ensure a fixed column
        header output that aligns with lists generated by INFO parsing.
        """
        info_names = list(self.info_schema.keys())
        info_names_in_order = sorted(info_names, 
                                     key=lambda info_name: 
                                        self.info_schema[info_name]['column_index'])
        return info_names_in_order

    def convert_info_to_columns(self, info_column_value):
        """Given a single INFO column value, return a list of the values it contains
        The list returned is ordered by the column index value specified in the
        info schema. It is crucially important that each INFO value input generates
        a list output of the same length and in the same order of its elements each time 
        it is called.
        Assumes INFO entries are separated by semi-colons.
        Some entries are key-value pairs, some are single value and other INFO names
        specified in the VCF header may not be in the given input. Each individual INFO entry
        is assumed to be a sub-set of all the INFO entries in the VCF header.
        This method deals with these scenarios by assigning 'X' to keys with no values
        and None to absent INFO IDs
        """
        info_elements = info_column_value.strip().split(';')
        # Some INFO columns contain empty values (";;"); this causes a key error where the key
        # '' does not exists. The following filter removes empty elements.
        info_elements = [info_element for info_element in info_elements 
                            if len(info_element.strip()) > 0]
        key, val = None, None
        extracted_values = [None] * len(list(self.info_schema.keys()))
        for info_element in info_elements:
            if '=' in info_element:
                key, val = info_element.split('=')
            else:
                key, val = info_element, 'X'
            column_position = self.info_schema[key]['column_index']
            extracted_values[column_position] = val
        return extracted_values

    def get_column_names_for_info_output_type(self, info_output_type):
        """Return a list of column names for output files.
        The info_output_type paramater can be either tab for when the output
        type file splits the INFO entries into separate columns or json when
        INFO is converted into a single-column JSON format.
        """
        column_names = ['chrom', 'position', 'variant_id', 'ref_allele', 'alt_allele']
        if info_output_type == 'tab':
            info_column_names = self.get_info_column_names_in_order()
            column_names.extend(info_column_names)
            return column_names
        elif info_output_type == 'json':
            column_names.append('info_json')
            return column_names
        else:
            raise ValueError('Expect value for info_output_type is"tab" or "json"')

    def convert_info_to_json(self, info_column_value):
        """Converts the given INFO input into JSON where INFO elements with key=value
        format are reresented as dictionary keys mapped to values and flags, that is entries
        not assigned by =, are appended to a list called 'flags'.
        """
        info_column_map = dict(flags = [])
        info_elements = info_column_value.strip().split(';')
        info_elements = [info_element for info_element in info_elements 
                            if len(info_element.strip()) > 0]
        key, val = None, None
        for info_element in info_elements:
            if '=' in info_element:
                key, val = info_element.split('=')
                info_column_map[key] = val
            else:
                info_column_map['flags'].append(info_element)
        return json.dumps(info_column_map)

    def _write_parsed_vcf_output(self, output_file, info_parsing_function, info_output_type):
        """Create a TSV of the VCF file with the INFO either broken into separate columns 
        for each INFO ID or with INFO converted into a single JSON string column. The INFO
        output format depends on the passed in method reference value and the value 
        of the 'info_output_type' argument
        VCF QUAL and FILTER columns are dropped. 
        """
        column_names = self.get_column_names_for_info_output_type(info_output_type)
        column_indexes_to_keep = [0, 1, 2, 3, 4, 7]
        row_start = False
        fho = open(output_file, 'wt')
        fho.write('\t'.join(column_names) + os.linesep)
        with open(self.vcf_file_path) as fh:
            csv_reader = csv.reader(fh, delimiter='\t', quotechar='"')
            for row in csv_reader:
                if row_start:
                    columns_keep =[row[i] for i in column_indexes_to_keep]
                    info_column = columns_keep.pop()
                    info_column_parsed = info_parsing_function(info_column)
                    # This check is used to determine which of list methods 'extend' or 'append'
                    #  is appropriate for adding the output from 'info_parsing_function' to list
                    # containing the other columns of the VCF row. 
                    if isinstance(info_column_parsed, list):
                        columns_keep.extend(info_column_parsed)
                        columns_keep = [str(column_value or '.') for column_value in columns_keep]
                    else:
                        columns_keep.append(info_column_parsed)
                    fho.write(('\t').join(columns_keep) + os.linesep)
                if row[0].startswith('#CHROM'):
                    row_start = True
        fho.close()

    def convert_vcf_to_tsv_output(self, output_file, info_output_type):
        """ Wraps the calls to the parsing methods for generating file output.
        The 'info_output_type' parameter determines which INFO parsing method is called.
        """
        if info_output_type == 'tab':
            self._write_parsed_vcf_output(output_file, self.convert_info_to_columns, info_output_type)
        elif info_output_type == 'json':
            self._write_parsed_vcf_output(output_file, self.convert_info_to_json, info_output_type)
        else:
            raise ValueError('Unrecognised info_output_type: {}'.format(info_output_type))

if __name__ == '__main__':
    from pprint import pprint
    dir_path = '{}/big_files/'.format(os.environ['HOME']) 
    vcf_file_path = os.path.join(dir_path, '1000GENOMES-phase_3.vcf')
    header_file_path = os.path.join(dir_path, 'vcf_header.txt')
    body_file_path = os.path.join(dir_path, 'vcf_body.tsv') 
    vcf2tsv = VCF2TSV(vcf_file_path)
    #vcf2tsv.write_header_to_file(header_file_path)
    #vcf2tsv.write_body_to_file(body_file_path)
    #pprint(vcf2tsv.generate_info_schema())
    #pprint(vcf2tsv.convert_info_to_columns('dbSNP_154;TSA=indel;E_Freq;E_1000G;E_TOPMed;AFR=0.4909;AMR=0.3602;EAS=0.3363;EUR=0.4056;SAS=0.4949'))
    #pprint(vcf2tsv.get_info_column_names_in_order())
    parsed_info_tsv_file_path_json = os.path.join(dir_path, 'parsed_vcf_info_json.tsv')
    vcf2tsv.convert_vcf_to_tsv_output(parsed_info_tsv_file_path_json, 'json')
    #pprint(vcf2tsv.convert_info_to_json('dbSNP_154;TSA=indel;E_Freq;E_1000G;E_TOPMed;AFR=0.4909;AMR=0.3602;EAS=0.3363;EUR=0.4056;SAS=0.4949'))
    #parsed_info_tsv_file_path_tabs = os.path.join(dir_path, 'parsed_vcf_info_1k_sample_tabs.tsv')
    #vcf2tsv.convert_vcf_to_tsv_output(parsed_info_tsv_file_path_tabs, 'tab')