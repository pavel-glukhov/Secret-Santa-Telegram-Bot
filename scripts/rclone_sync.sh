#!/bin/bash
set -e

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PROJECT_DIR=$(dirname "$SCRIPT_DIR")
ENV_FILE="$PROJECT_DIR/.env"

export $(grep -v '^#' "$ENV_FILE" | xargs)
cd "$SCRIPT_DIR" || exit 1

docker run --rm \
  -v "$BACKUP_ROOT:/data:ro" \
  -v "$PROJECT_DIR/config/rclone/rclone.conf:/config/rclone/rclone.conf:ro" \
  -v "$PROJECT_DIR/config/rclone/gdrive_key.json:/config/rclone/gdrive_key.json:ro" \
  -e RCLONE_CONFIG=/config/rclone/rclone.conf \
  rclone/rclone:latest copy /data gdrive:db_backup --verbose

if [ $? -ne 0 ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
         -d "chat_id=${TELEGRAM_CHAT_ID}" \
         -d "text=❌ Error uploading backups to Google Drive"
    exit 1
fi

echo "✅ Backups uploaded to Google Drive successfully"
