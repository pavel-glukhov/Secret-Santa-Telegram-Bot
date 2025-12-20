#!/bin/bash

# ==============================================================================
# REDIS BACKUP SCRIPT (DOCKER)
# ==============================================================================
#
# DESCRIPTION:
# This script backups Redis by forcing a snapshot (SAVE) and copying the
# 'dump.rdb' file. It supports:
# 1) LOCAL  - Storage in /backups/redis/
# 2) GDRIVE - Upload via rclone
# 3) RSYNC  - Transfer via SSH
# 4) ALL    - All of the above
#
# --- SETUP INSTRUCTIONS ---
#
# 1. PERMISSIONS:
#    - 'chmod +x redis_backup.sh'
#
# 2. GOOGLE DRIVE / RSYNC:
#    - Follow the same setup as the PostgreSQL script (rclone config / ssh-copy-id).
#
# 3. DOCKER NOTE:
#    - This script uses 'docker exec redis-cli SAVE' to ensure data consistency.
#
# ==============================================================================

# --- CONFIGURATION ---

# HARD CHOICE: Set your backup type here ("local", "gdrive", "rsync", "all")
BACKUP_TYPE="local"

# General Settings
BACKUP_DIR="/backups/redis"
DAYS_TO_KEEP=30
FILE_SUFFIX="_redis_backup.rdb"
CONTAINER_NAME="your_redis_container_name"

# Google Drive Settings
GDRIVE_REMOTE="remote_gdrive"
GDRIVE_DIR="backups/redis"

# Rsync / Remote Host Settings
REMOTE_USER="user"
REMOTE_HOST="1.2.3.4"
REMOTE_DIR="/home/user/backups/redis/"

# --- INTERNAL VARIABLES ---
TIMESTAMP=$(date +"%Y%m%d%H%M")
FILE="${TIMESTAMP}${FILE_SUFFIX}"
OUTPUT_FILE="${BACKUP_DIR}/${FILE}"
GZ_FILE="${OUTPUT_FILE}.gz"

# --- BACKUP LOGIC ---

create_rdb_snapshot() {
    echo "$(date): [LOG] Triggering Redis SAVE command..."
    # Force Redis to write memory to disk
    docker exec "${CONTAINER_NAME}" redis-cli SAVE

    if [ $? -ne 0 ]; then
        echo "$(date): [ERROR] Failed to execute SAVE in Redis container!"
        exit 1
    fi

    echo "$(date): [LOG] Copying dump.rdb from container..."
    mkdir -p "$BACKUP_DIR"

    # Copying the file directly from the container's data volume
    docker cp "${CONTAINER_NAME}":/data/dump.rdb "${OUTPUT_FILE}"

    if [ $? -eq 0 ]; then
        gzip -f "${OUTPUT_FILE}"
        echo "$(date): [LOG] Redis backup compressed: $GZ_FILE"
    else
        echo "$(date): [ERROR] Failed to copy dump.rdb!"
        exit 1
    fi
}

# --- EXECUTION MODES ---

case "$BACKUP_TYPE" in
    "local")
        echo "$(date): [MODE] Local backup selected."
        create_rdb_snapshot
        ;;

    "gdrive")
        echo "$(date): [MODE] Google Drive backup selected."
        create_rdb_snapshot
        echo "$(date): [LOG] Uploading to Google Drive..."
        rclone copy "$GZ_FILE" "${GDRIVE_REMOTE}:${GDRIVE_DIR}"
        rclone delete --min-age "${DAYS_TO_KEEP}d" "${GDRIVE_REMOTE}:${GDRIVE_DIR}"
        ;;

    "rsync")
        echo "$(date): [MODE] Rsync remote backup selected."
        create_rdb_snapshot
        echo "$(date): [LOG] Syncing to remote host..."
        rsync -avz -e ssh "$GZ_FILE" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"
        ;;

    "all")
        echo "$(date): [MODE] Full distribution backup selected."
        create_rdb_snapshot
        rclone copy "$GZ_FILE" "${GDRIVE_REMOTE}:${GDRIVE_DIR}"
        rsync -avz -e ssh "$GZ_FILE" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"
        ;;

    *)
        echo "$(date): [ERROR] Invalid BACKUP_TYPE."
        exit 1
        ;;
esac

# --- LOCAL CLEANUP ---
echo "$(date): [LOG] Cleaning up local files older than $DAYS_TO_KEEP days..."
find "$BACKUP_DIR" -maxdepth 1 -mtime +"$DAYS_TO_KEEP" -name "*${FILE_SUFFIX}.gz" -exec rm -rf '{}' ';'

echo "$(date): [LOG] Redis backup finished successfully."