#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PROJECT_DIR=$(dirname "$SCRIPT_DIR")
ENV_FILE="$PROJECT_DIR/.env"

export $(grep -v '^#' "$ENV_FILE" | xargs)

cd "$SCRIPT_DIR" || exit 1

mkdir -p "${BACKUP_ROOT}/postgres"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_ROOT}/postgres/db_backup_$TIMESTAMP.sql"
BACKUP_FILE_GZ="${BACKUP_FILE}.gz"

docker exec db pg_dump -U "$DATABASE_USER" -d "$DATABASE_NAME" > "$BACKUP_FILE"
if [ $? -ne 0 ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
         -d "chat_id=${TELEGRAM_CHAT_ID}" \
         -d "text=❌ PostgreSQL dump error"
    exit 1
fi

gzip "$BACKUP_FILE"
if [ $? -ne 0 ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
         -d "chat_id=${TELEGRAM_CHAT_ID}" \
         -d "text=❌ PostgreSQL compression error"
    exit 1
fi

find "${BACKUP_ROOT}/postgres" -name "*.sql.gz" -type f -mtime +7 -delete

echo "✅ PostgreSQL backup saved to $BACKUP_FILE_GZ"
