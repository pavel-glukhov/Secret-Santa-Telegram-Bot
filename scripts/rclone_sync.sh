#!/bin/bash
PROJECT_DIR="/opt/secret-santa-bot"
cd "$PROJECT_DIR"
export $(grep -v '^#' .env.dev | xargs)

docker run --rm \
  -v "$PROJECT_DIR/backups:/data:ro" \
  -v "$PROJECT_DIR/rclone.conf:/config/rclone/rclone.conf:ro" \
  -v "$PROJECT_DIR/gdrive_key.json:/config/rclone/gdrive_key.json:ro" \
  rclone/rclone:latest copy /data gdrive:db_backup --verbose

if [ $? -ne 0 ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
         -d "chat_id=${TELEGRAM_CHAT_ID}" \
         -d "text=❌ Error of uploading backups in Google Drive"
    exit 1
fi