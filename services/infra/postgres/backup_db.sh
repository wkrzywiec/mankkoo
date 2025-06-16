#!/bin/bash
set -e

DB_NAME=${1:-mankkoo}
BACKUP_DIR="/tmp"
TS=$(date +"%Y%m%d_%H%M")
BACKUP_FILE="${DB_NAME}_${TS}.dump.gz"
DUMP_PATH="${BACKUP_DIR}/${DB_NAME}_backup.dump"

export PGPASSWORD=postgres

# Create dump
/usr/bin/pg_dump -U postgres "$DB_NAME" -F c -b -v -f "$DUMP_PATH"

# Compress
gzip -9 "$DUMP_PATH"

# Rename
mv "${DUMP_PATH}.gz" "${BACKUP_DIR}/$BACKUP_FILE"

echo "$BACKUP_FILE"
