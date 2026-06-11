FROM ubuntu:22.04

RUN apt-get update && apt-get install -y vsftpd && rm -rf /var/lib/apt/lists/*

COPY vsftpd.conf /etc/vsftpd.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN useradd -m -s /bin/bash ftpuser && echo "ftpuser:friends" | chpasswd
RUN (useradd -m -s /bin/bash backup 2>/dev/null || usermod -m -d /home/backup -s /bin/bash backup) && echo "backup:backup123" | chpasswd

RUN mkdir -p /home/ftpuser/public /home/backup/backups

# Flag in user home directory (visible on ls)
RUN printf "FLAG{b2r_ftp_brute_force_c5a0}\n\nCredentials found:\n  SMB: smbuser / P@ssw0rd\n\nNext: Try connecting to SMB (port 445)\n" > /home/ftpuser/flag.txt

RUN printf "Welcome to Bot2Root FTP Server\n\nNothing sensitive here... or is there?\nCheck your home directory carefully.\n" > /home/ftpuser/public/readme.txt
RUN printf "server_backup_2026-04-30.tar.gz - corrupted\ndb_dump.sql - moved to SMB share\n" > /home/backup/backups/backup_log.txt
RUN echo "FLAG{b2r_ftp_backup_user_f1b7}" > /home/backup/backups/.flag.txt

RUN chown -R ftpuser:ftpuser /home/ftpuser
RUN chown -R backup:backup /home/backup

RUN mkdir -p /var/run/vsftpd/empty

EXPOSE 21 30000-30029

ENTRYPOINT ["/entrypoint.sh"]
