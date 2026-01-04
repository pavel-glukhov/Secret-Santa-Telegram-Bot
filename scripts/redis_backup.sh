#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PROJECT_DIR=$(dirname "$SCRIPT_DIR")
ENV_FILE="$PROJECT_DIR/.env"

export $(grep -v '^#' "$ENV_FILE" | xargs)

cd "$SCRIPT_DIR" || exit 1

mkdir -p "$BACKUP_ROOT/redis"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_ROOT/redis/redis_$TIMESTAMP.rdb"

docker exec redis redis-cli -a "$REDIS_PASSWORD" --no-auth-warning SAVE
if [ $? -ne 0 ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
         -d "chat_id=${TELEGRAM_CHAT_ID}" \
         -d "text=❌ Redis SAVE command failed"
    exit 1
fi

docker cp redis:/data/dump.rdb "$BACKUP_PATH"
if [ $? -ne 0 ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
         -d "chat_id=${TELEGRAM_CHAT_ID}" \
         -d "text=❌ Redis backup copy failed"
    exit 1
fi

gzip "$BACKUP_PATH"
if [ $? -ne 0 ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
         -d "chat_id=${TELEGRAM_CHAT_ID}" \
         -d "text=❌ Redis backup compression failed"
    exit 1
fi

echo "✅ Redis backup saved to $BACKUP_PATH.gz"
