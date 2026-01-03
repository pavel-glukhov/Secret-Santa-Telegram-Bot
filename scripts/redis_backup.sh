#!/bin/bash
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
cd "SCRIPT_DIR"
export $(grep -v '^#' .env.dev | xargs)

TIMESTAMP=$(date +%Y%m%d)
BACKUP_PATH="./backups/redis/redis_$TIMESTAMP.rdb"

docker exec redis redis-cli -a "$REDIS_PASSWORD" --no-auth-warning SAVE && \
docker cp redis:/data/dump.rdb "$BACKUP_PATH"

if [ $? -ne 0 ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
         -d "chat_id=${TELEGRAM_CHAT_ID}" \
         -d "text=❌ Redis backup error"
    exit 1
fi