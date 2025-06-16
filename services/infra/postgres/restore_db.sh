#!/bin/bash
set -e

BACKUP_FILE=$1
DB_NAME=${2:-mankkoo}
BACKUP_DIR="/tmp"

if [[ -z "$BACKUP_FILE" ]]; then
  echo "Usage: $0 <backup_file> [db_name]"
  exit 1
fi

export PGPASSWORD=postgres

# Unpack backup
gunzip -f "$BACKUP_DIR/$BACKUP_FILE.dump.gz"

# Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME WITH (FORCE);"
psql -U postgres -c "CREATE DATABASE $DB_NAME;"

# Restore backup
pg_restore -U postgres -d "$DB_NAME" -v "$BACKUP_DIR/$BACKUP_FILE.dump"

# Clean up
rm -f "$BACKUP_DIR/$BACKUP_FILE.dump"
