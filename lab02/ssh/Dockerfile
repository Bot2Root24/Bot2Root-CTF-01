FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    openssh-server \
    curl \
    redis-tools \
    net-tools \
    nmap \
    cron \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create developer user (credentials leaked via SSRF)
RUN useradd -m -s /bin/bash developer && echo "developer:dev_2026_bot2root!" | chpasswd

# LOLBin privesc: developer can run nmap as root (GTFOBins)
# https://gtfobins.github.io/gtfobins/nmap/
RUN echo "developer ALL=(root) NOPASSWD: /usr/bin/nmap" > /etc/sudoers.d/developer
RUN chmod 440 /etc/sudoers.d/developer

# Set strong root password (not guessable, must use LOLBin)
RUN echo "root:X#k9\$mR2!vL7@pQ4wZ&nB5" | chpasswd

RUN mkdir -p /var/run/sshd
RUN sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
# Disable SFTP to prevent file uploads
RUN sed -i 's/^Subsystem.*sftp.*/#&/' /etc/ssh/sshd_config

# Cron job for healthcheck
RUN echo "*/2 * * * * root curl -s http://10.10.3.10:3000/api/health > /dev/null 2>&1" > /etc/cron.d/healthcheck
RUN chmod 644 /etc/cron.d/healthcheck

# Developer flag (SSH pivot achieved)
RUN echo "FLAG{b2r_ssh_pivot_access_a3d5}\n\n=== Lab02 Access Achieved ===\n\nYou've pivoted into the internal network!\n\nRecon tips:\n  - Check what you can run with elevated privileges: sudo -l\n  - Redis is nearby (10.10.3.30:6379) - no auth!\n  - Explore the lab03 network (10.10.3.0/24)\n\nNext: Escalate to root on this machine." > /home/developer/flag.txt
RUN chown developer:developer /home/developer/flag.txt

# Redis sync script (populates redis with hints)
RUN echo '#!/bin/bash\nredis-cli -h 10.10.3.30 SET admin_note "developer has sudo nmap - check GTFOBins" 2>/dev/null\nredis-cli -h 10.10.3.30 SET api_key "bot2root-internal-api-key-2026" 2>/dev/null\nredis-cli -h 10.10.3.30 SET lab03_services "metadata:10.10.3.50 redis:10.10.3.30 java:10.10.3.20" 2>/dev/null' > /opt/redis_sync.sh
RUN chmod 755 /opt/redis_sync.sh

# Root flag (final - only accessible after LOLBin privesc)
RUN echo "FLAG{b2r_final_root_lab02_7e9b}\n\n====================================================\n     CONGRATULATIONS - BOT2ROOT CTF COMPLETE!\n====================================================\n\nYou successfully:\n  1. Bypassed SQLi WAF + Rate Limit on the web app\n  2. Exploited stored DOM XSS\n  3. Achieved RCE via file upload filter bypass\n  4. Brute-forced FTP credentials\n  5. Enumerated SMB shares for intel\n  6. Cracked IKE VPN PSK (password reuse)\n  7. Escalated privileges on Lab01 (SUID + cron)\n  8. Pivoted to Lab02 via SSH local port forwarding\n  9. Chained SSRF to leak credentials from internal API\n  10. Used LOLBin (nmap GTFOBins) for root escalation\n\nFLAG{b2r_ctf_complete_2f6c}\n\nReport your findings to the instructor." > /root/root.txt
RUN chmod 400 /root/root.txt

# === SECURITY HARDENING ===
# Remove scp to prevent file uploads
RUN rm -f /usr/bin/scp
# Remove python3 to prevent exploit scripts
RUN apt-get purge -y python3 python3-minimal 2>/dev/null; \
    apt-get autoremove -y 2>/dev/null; \
    rm -f /usr/bin/python3 /usr/bin/python; true
# Remove wget
RUN rm -f /usr/bin/wget
# Remove perl/ruby to prevent alternative script execution
RUN rm -f /usr/bin/perl /usr/bin/perl5* /usr/bin/ruby 2>/dev/null; \
    apt-get purge -y perl-base 2>/dev/null; true

EXPOSE 22

CMD ["sh", "-c", "service cron start && /opt/redis_sync.sh 2>/dev/null; /usr/sbin/sshd -D"]
