#!/bin/bash
PROJECT_DIR="/opt/secret-santa-bot"
cd "$PROJECT_DIR"
export $(grep -v '^#' .env.dev | xargs)

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="./backups/postgres/db_backup_$TIMESTAMP.sql"

docker exec db pg_dump -U "$DATABASE_USER" -d "$DATABASE_NAME" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    find ./backups/postgres -name "*.sql" -type f -mtime +7 -delete
else
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
         -d "chat_id=${TELEGRAM_CHAT_ID}" \
         -d "text=❌ Error of PostgreSQL dump"
    exit 1
fi