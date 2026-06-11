FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    openssh-server \
    strongswan \
    strongswan-starter \
    libcharon-extra-plugins \
    sudo \
    nano \
    vim \
    net-tools \
    curl \
    nmap \
    sshpass \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Create ike user with VPN PSK as password (password reuse vulnerability)
RUN useradd -m -s /bin/bash ike && echo "ike:freakingrockstarontheroad" | chpasswd

# Create a low-priv user for initial limited shell
RUN useradd -m -s /bin/rbash restricted && echo "restricted:restricted" | chpasswd

# SSH configuration
RUN mkdir -p /var/run/sshd
COPY sshd_config /etc/ssh/sshd_config

# Configure strongSwan IKE (intentionally misconfigured - Aggressive mode with weak PSK)
COPY ipsec.conf /etc/ipsec.conf
COPY ipsec.secrets /etc/ipsec.secrets

# User flag
RUN echo "FLAG{b2r_ike_password_reuse_7b5e}\n\nCongratulations! You exploited IKE VPN PSK reuse.\nThe PSK 'freakingrockstarontheroad' was reused for SSH.\n\nNext: Escalate to root. Check for binaries and cron." > /home/ike/user.txt
RUN chown ike:ike /home/ike/user.txt
RUN chmod 400 /home/ike/user.txt

# Privilege escalation setup
# 1. SUID binary - custom binary that reads files as root (blocks root_flag_02)
COPY privesc/readfile.c /tmp/readfile.c
RUN apt-get update && apt-get install -y gcc && \
    gcc -o /usr/local/bin/readfile /tmp/readfile.c && \
    chmod u+s /usr/local/bin/readfile && \
    rm /tmp/readfile.c && \
    apt-get remove -y gcc && apt-get autoremove -y

# 2. Cron job running as root with writable script
RUN echo "#!/bin/bash\n# Maintenance script\ncd /opt/maintenance\nfor f in *.sh; do bash \"\$f\"; done" > /opt/run_maintenance.sh
RUN chmod 755 /opt/run_maintenance.sh
RUN mkdir -p /opt/maintenance && chmod 777 /opt/maintenance
RUN echo "* * * * * root /opt/run_maintenance.sh" > /etc/cron.d/maintenance
RUN chmod 644 /etc/cron.d/maintenance

# Root flag 01 — in /home/restricted (SUID readfile path)
# Only root can read it; ike user must use the SUID readfile binary
RUN echo "FLAG{b2r_suid_privesc_root_flag01_e9a2}\n\n=== ROOT FLAG 01 ===\nYou used a SUID binary to read this file.\nBut can you get actual command execution as root?\n\nHint: The second root flag is at /root/root_flag_02.txt\nThe readfile binary CANNOT access it.\nLook for scheduled tasks running as root - can you abuse them?" > /home/restricted/root_flag_01.txt
RUN chown root:root /home/restricted/root_flag_01.txt
RUN chmod 400 /home/restricted/root_flag_01.txt

# Root flag 02 — in /root (cron job path ONLY) — contains Lab02 pivoting guide
# readfile binary explicitly blocks this file; only cron job can copy it out
RUN echo "FLAG{b2r_cron_privesc_root_flag02_1c4d}\n\n=== CONGRATULATIONS - ROOT ACCESS ON LAB01 ===\n\nYou've fully compromised Lab01!\n\nLab02 Information:\n==================\nNetwork: 10.10.2.0/24 (accessible via gateway 10.10.1.254)\nGateway password: g4t3w4y_b0t2r00t\n\nServices behind gateway:\n  - API Server: 10.10.2.10:3000 (has SSRF vulnerability)\n  - SSH Target: 10.10.2.40:22\n\nPivoting Guide:\n===============\nUse SSH Local Port Forwarding to reach lab02 services:\n\n  Step 1: Forward API port through gateway:\n    ssh -L 3000:10.10.2.10:3000 root@10.10.1.254\n\n  Step 2: Now access the API locally:\n    curl http://127.0.0.1:3000/\n\n  Step 3: Forward SSH port for lab02-ssh:\n    ssh -L 2240:10.10.2.40:22 root@10.10.1.254\n    ssh developer@127.0.0.1 -p 2240\n\nAlternative: Dynamic SOCKS proxy:\n    ssh -D 1080 -N root@10.10.1.254\n    proxychains curl http://10.10.2.10:3000/\n\nStart with the API server - enumerate its endpoints!\n\nFLAG{b2r_lab02_pivot_guide_5f83}" > /root/root_flag_02.txt
RUN chmod 400 /root/root_flag_02.txt

# === SECURITY HARDENING ===
# Remove scp to prevent file uploads via SSH
RUN rm -f /usr/bin/scp

# Remove python3 to prevent running exploit scripts
RUN apt-get purge -y python3 python3-pip python3-minimal 2>/dev/null; \
    apt-get autoremove -y 2>/dev/null; \
    rm -f /usr/bin/python3 /usr/bin/python; true

# Remove wget to prevent downloading external tools (curl kept for pivoting)
RUN rm -f /usr/bin/wget

# Remove compilers/interpreters that could be used for exploits
RUN rm -f /usr/bin/perl /usr/bin/ruby 2>/dev/null; true

# Gateway SSH key for pivoting
RUN mkdir -p /root/.ssh

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22 500/udp 4500/udp

ENTRYPOINT ["/entrypoint.sh"]
