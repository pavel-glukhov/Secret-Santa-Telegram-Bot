#!/bin/bash
echo "Starting backup environment setup..."

# 1. Create directories
echo "Creating backup folders..."
mkdir -p backups/postgres
mkdir -p backups/redis
# 2. Create config files if they don't exist
echo "Checking configuration files..."

if [ ! -f rclone.conf ]; then
    echo "Creating rclone.conf..."
    cat <<EOF > rclone.conf
[gdrive]
type = drive
scope = drive
service_account_file = /config/rclone/gdrive_key.json
EOF
fi

if [ ! -f gdrive_key.json ]; then
    echo "Creating empty gdrive_key.json..."
    echo "{}" > gdrive_key.json
fi

echo "Setting permissions..."
chmod -R 754 backups

echo "Done!"
echo "Next steps:"
echo "1. Paste your Service Account JSON into gdrive_key.json"
echo "2. Run 'docker compose up -d' or select necessary compose config with -f key"