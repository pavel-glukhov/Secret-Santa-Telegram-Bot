#!/bin/bash
#
# Backup a Postgresql database
#

BACKUP_DIR=/backups/database/
DAYS_TO_KEEP=30
FILE_SUFFIX=_db_backup.sql
DATABASE=procharrity
USER=postgres

FILE=`date +"%Y%m%d%H%M"`${FILE_SUFFIX}
OUTPUT_FILE=${BACKUP_DIR}/${FILE}
pg_dump -U ${USER} ${DATABASE} -F p -f ${OUTPUT_FILE}
gzip $OUTPUT_FILE
find $BACKUP_DIR -maxdepth 1 -mtime +$DAYS_TO_KEEP -name "*${FILE_SUFFIX}.gz" -exec rm -rf '{}' ';'