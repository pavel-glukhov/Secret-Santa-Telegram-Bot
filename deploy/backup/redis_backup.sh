#!/bin/bash
#
# Backup the redis database
#
REDIS_VOLUME_PATH=$(docker volume inspect redis_data | grep Mountpoint | awk -F'"' '{print $4}')
BACKUP_DIR="/backups/redis/"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/redis_backup_$TIMESTAMP.rdb"

cp "$REDIS_VOLUME_PATH/dump.rdb" "$BACKUP_FILE"

find "$BACKUP_DIR" -type f -name "redis_backup_*.rdb" -mtime +7 -delete

echo "Backup of redis DB has been completed: $BACKUP_FILE"