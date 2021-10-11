#!/bin/bash

# Given four arguments (checks for this):
# 1. The name of the SQLite DB - full path or it will be created in the directory where the 
#   script is run
# 2., 3., and 4. The names of the file contaning the variant detals, the the INFO key-val pairs 
#   and the INFO flags
# Warning: Removes the SQLite file of that name if it already exists!
# Assumes the SQL scripts it uses are in the dame directory as this shell script
# Uses a HEREDOC to execute a series of SQLite commands to:
# - Set the mode to tabs (assuming the input files are tab-delimited!)
# - Set headers on
# - Execute an external SQL DDL script to create the tables
# - Three import statements import the files into the tables just created
# - Split the INFO key-value data into string and numeric by executing an external SQL script
# - Create the indexes
# - Run the VACUUM command to ensure that the database is cleaned up after splitting the info data when a large DELETE
#     of duplicate data is performed.
# Examle invocation:  ~/mybix/files2sqlite.sh sample_1k_vcf.db 1000GENOMES-phase_3_1k_sample_variant_details.txt 1000GENOMES-phase_3_1k_sample_info_keys_vals.txt 1000GENOMES-phase_3_1k_sample_info_flags.txt

# Set the directory to the one where this script is located. Used to read in SQL scripts.
SCRIPT_DIR=$(dirname "$0")

# Ensure the correct number of arguments is passed to the script
if [ "$#" -ne 4 ]; then
    echo "Error! Expected four arguments got $# Exiting!"
    exit 1

fi
SQLITE_DB_NAME=$1
FILE_VARIANT_DETAILS=$2
FILE_INFO_KEY_VAL=$3
FILE_INFO_FLAG=$4
SQL_DDL_FILE=$SCRIPT_DIR/vcf_ddl.sql
SQL_INDEX_FILE=$SCRIPT_DIR/indexes.sql
SQL_INFO_NUM_MOVE_FILE=$SCRIPT_DIR/info_numeric_value_move.sql
# Warning: Removes SQLite DB if it already exists!
[ ! -e $SQLITE_DB_NAME ] || rm $SQLITE_DB_NAME
# Execute SQLite commands
sqlite3 $SQLITE_DB_NAME <<EOF
pragma journal_mode = WAL;
pragma synchronous = normal;
pragma temp_store = memory;
pragma mmap_size = 30000000000;
.mode tabs
.headers on
.read $SQL_DDL_FILE
.import $FILE_VARIANT_DETAILS variant_detail
.import $FILE_INFO_KEY_VAL info_key_val
.import $FILE_INFO_FLAG info_flag
.read $SQL_INFO_NUM_MOVE_FILE 
.read $SQL_INDEX_FILE
DROP TABLE info_key_val;
VACUUM;
.quit
EOF

