#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "Error! Expected two arguments got $# Exiting!"
    exit 1

fi
SQLITE_DB_NAME=$1
FILE_VARIANT_DETAILS=$2
FILE_INFO_KEY_VAL=$3
FILE_INFO_FLAG=$4
SQL_DDL_FILE=$HOME/mybix/vcf_ddl.sql
SQL_INDEX_FILE=$HOME/mybix/indexes.sql
# Warning: Removes SQLite DB if it already exists!
[ ! -e $SQLITE_DB_NAME ] || rm $SQLITE_DB_NAME

sqlite3 $SQLITE_DB_NAME <<EOF
.mode tabs
.headers on
.read $SQL_DDL_FILE
.import $FILE_VARIANT_DETAILS variant_detail
.import $FILE_INFO_KEY_VAL info_key_val
.import $FILE_INFO_FLAG info_flag
.read $SQL_INDEX_FILE
.quit
EOF

