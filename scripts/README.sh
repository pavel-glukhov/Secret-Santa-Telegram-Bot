chmod +x scripts/*.sh
crontab -e

0 0 * * * /bin/bash /home/user/your_project/scripts/db_backup.sh >> /opt/secret-santa-bot/backups/db.log 2>&1
30 0 * * * /bin/bash /home/user/your_project/scripts/redis_backup.sh >> /opt/secret-santa-bot/backups/redis.log 2>&1
30 1 * * * /bin/bash /home/user/your_project/scripts/rclone_sync.sh >> /opt/secret-santa-bot/backups/rclone.log 2>&1