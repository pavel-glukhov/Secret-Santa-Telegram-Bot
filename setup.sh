#!/bin/bash

PROJECT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
export $(grep -v '^#' .env | xargs)

echo "--- Project Initialization (Secure Version) ---"

sudo mkdir -p "$BACKUP_ROOT/postgres" "$BACKUP_ROOT/redis"
sudo chown -R deployer:deployer "$BACKUP_ROOT"
chmod -R 770 "$BACKUP_ROOT"

echo "Configuring crontab..."
CRON_TASKS=(
"0 0 * * * /bin/bash $PROJECT_DIR/scripts/db_backup.sh >> $BACKUP_ROOT/postgres_history.log 2>&1"
"30 0 * * * /bin/bash $PROJECT_DIR/scripts/redis_backup.sh >> $BACKUP_ROOT/redis_history.log 2>&1"
"30 1 * * * /bin/bash $PROJECT_DIR/scripts/rclone_sync.sh >> $BACKUP_ROOT/sync_history.log 2>&1"
)


CURRENT_CRON=$(crontab -l 2>/dev/null)
UPDATED=false

for TASK in "${CRON_TASKS[@]}"; do
    if ! echo "$CURRENT_CRON" | grep -Fq "$TASK"; then
        CURRENT_CRON=$(echo -e "$CURRENT_CRON\n$TASK")
        UPDATED=true
    fi
done

if [ "$UPDATED" = true ]; then
    echo "$CURRENT_CRON" | sed '/^$/d' | crontab -
    echo "Crontab updated."
fi

echo "--- Project Init Done! ---"