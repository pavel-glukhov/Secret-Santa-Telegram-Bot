#!/bin/bash

# ==============================================================================
# DATABASE BACKUP SCRIPT (DOCKER POSTGRESQL)
# ==============================================================================
#
# DESCRIPTION:
# This script performs a backup of a PostgreSQL database running inside a
# Docker container and provides 4 storage options:
# 1) LOCAL  - Keep backup only on this server.
# 2) GDRIVE - Upload to Google Drive using 'rclone'.
# 3) RSYNC  - Transfer to a remote server via SSH.
# 4) ALL    - Perform all of the above.
#
# --- SETUP INSTRUCTIONS ---
#
# 1. PERMISSIONS:
#    - Before running, make the script executable:
#      'chmod +x backup_script.sh'
#
# 2. LOCAL SETUP:
#    - Ensure the BACKUP_DIR exists or the script has permissions to create it.
#
# 3. GOOGLE DRIVE SETUP (rclone):
#    - Install rclone: 'curl https://rclone.org/install.sh | sudo bash'
#    - Run 'rclone config' and follow the steps:
#      a) New remote: Name it "remote_gdrive".
#      b) Storage type: Choose "drive" (Google Drive).
#      c) Follow the OAuth process to link your account.
#
# 4. RSYNC (REMOTE HOST) SETUP:
#    - Ensure the remote server has SSH access.
#    - Setup Passwordless SSH:
#      a) On THIS server, run: 'ssh-keygen -t rsa' (press Enter for all).
#      b) Copy key to remote: 'ssh-copy-id user@remote_host_ip'.
#    - The script will now login to the remote host without asking for a password.
#
# 5. CRONTAB AUTOMATION:
#    - Open crontab: 'crontab -e'
#    - Add: '00 02 * * * /path/to/backup_script.sh >> /var/log/db_backup.log 2>&1'
#
# ==============================================================================

# --- CONFIGURATION ---

# HARD CHOICE: Set your backup type here ("local", "gdrive", "rsync", "all")
BACKUP_TYPE="local"

# General Settings
BACKUP_DIR="/backups/database"      # Where to store backups locally
DAYS_TO_KEEP=30                     # Retention period for old backups
FILE_SUFFIX="_db_backup.sql"        # Filename suffix
DATABASE="NAME_DB"                  # Your database name
USER="postgres"                     # Database username
CONTAINER_NAME="your_container"     # Docker container name

# Google Drive Settings
GDRIVE_REMOTE="remote_gdrive"       # Name of the rclone remote
GDRIVE_DIR="backups/sql"            # Folder path in GDrive

# Rsync / Remote Host Settings
REMOTE_USER="user"                  # Remote server username
REMOTE_HOST="1.2.3.4"               # Remote server IP/Hostname
REMOTE_DIR="/home/user/backups/"    # Destination path on remote server

# --- INTERNAL VARIABLES ---
TIMESTAMP=$(date +"%Y%m%d%H%M")
FILE="${TIMESTAMP}${FILE_SUFFIX}"
OUTPUT_FILE="${BACKUP_DIR}/${FILE}"
GZ_FILE="${OUTPUT_FILE}.gz"

# --- BACKUP LOGIC ---

create_dump() {
    echo "$(date): [LOG] Starting backup for database: $DATABASE"

    # Create directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"

    # Execute dump. Using redirection (>) to ensure file is saved on the Host, not inside Container
    docker exec -t "${CONTAINER_NAME}" pg_dump -U "${USER}" "${DATABASE}" -F p > "${OUTPUT_FILE}"

    if [ $? -eq 0 ]; then
        gzip -f "${OUTPUT_FILE}"
        echo "$(date): [LOG] Dump successfully created and compressed: $GZ_FILE"
    else
        echo "$(date): [ERROR] Database dump failed!"
        exit 1
    fi
}

# --- EXECUTION MODES ---

case "$BACKUP_TYPE" in
    "local")
        echo "$(date): [MODE] Local backup selected."
        create_dump
        ;;

    "gdrive")
        echo "$(date): [MODE] Google Drive backup selected."
        create_dump
        echo "$(date): [LOG] Uploading to Google Drive..."
        rclone copy "$GZ_FILE" "${GDRIVE_REMOTE}:${GDRIVE_DIR}"
        # Cleanup old backups in Google Drive
        rclone delete --min-age "${DAYS_TO_KEEP}d" "${GDRIVE_REMOTE}:${GDRIVE_DIR}"
        ;;

    "rsync")
        echo "$(date): [MODE] Rsync remote backup selected."
        create_dump
        echo "$(date): [LOG] Syncing to remote host via Rsync..."
        rsync -avz -e ssh "$GZ_FILE" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"
        ;;

    "all")
        echo "$(date): [MODE] Full distribution backup selected (Local, GDrive, Rsync)."
        create_dump
        echo "$(date): [LOG] Uploading to Google Drive..."
        rclone copy "$GZ_FILE" "${GDRIVE_REMOTE}:${GDRIVE_DIR}"
        echo "$(date): [LOG] Syncing to remote host..."
        rsync -avz -e ssh "$GZ_FILE" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"
        ;;

    *)
        echo "$(date): [ERROR] Invalid BACKUP_TYPE. Please use: local, gdrive, rsync, or all."
        exit 1
        ;;
esac

# --- LOCAL CLEANUP ---
# Delete local files older than X days
echo "$(date): [LOG] Cleaning up local files older than $DAYS_TO_KEEP days..."
find "$BACKUP_DIR" -maxdepth 1 -mtime +"$DAYS_TO_KEEP" -name "*${FILE_SUFFIX}.gz" -exec rm -rf '{}' ';'

echo "$(date): [LOG] Backup process finished successfully."