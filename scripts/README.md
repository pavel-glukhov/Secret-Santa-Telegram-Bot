Small scripts for backing up PostgreSQL and Redis databases, intended to be added to cron. 
The scripts perform the backup, upload copies to Google Drive, clean up backups older than 7 days, and send a Telegram notification in case of any errors.


```bash
chmod +x scripts/*.sh
crontab -e
```

```bash
0 0 * * * /bin/bash /opt/secret-santa-bot/scripts/db_backup.sh >> /var/backups/secret-santa-bot/db.log 2>&1
30 0 * * * /bin/bash /opt/secret-santa-bot/scripts/redis_backup.sh >> /var/backups/secret-santa-bot/redis.log 2>&1
30 1 * * * /bin/bash /opt/secret-santa-bot/scripts/rclone_sync.sh >> /var/backups/secret-santa-bot/rclone.log 2>&1
```