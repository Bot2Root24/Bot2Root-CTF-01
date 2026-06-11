FROM ubuntu:22.04

RUN apt-get update && apt-get install -y samba && rm -rf /var/lib/apt/lists/*

COPY smb.conf /etc/samba/smb.conf

# Create users and set Samba passwords using pdbedit (works without smbd running)
RUN useradd -m smbuser && \
    (echo "P@ssw0rd"; echo "P@ssw0rd") | smbpasswd -s -a smbuser
RUN useradd -m smbadmin && \
    (echo "admin2023!"; echo "admin2023!") | smbpasswd -s -a smbadmin

# Allow smbuser to access confidential share (owned by smbadmin group)
RUN usermod -aG smbadmin smbuser

RUN mkdir -p /srv/samba/public /srv/samba/confidential /srv/samba/backup
RUN printf "Welcome to Bot2Root SMB shares\n\nAvailable shares:\n  - public (guest)\n  - confidential (authenticated)\n  - backup (hidden)\n" > /srv/samba/public/readme.txt
RUN printf "FLAG{b2r_smb_share_enum_92de}\n\nVPN Configuration Found!\n  IKE Server: 10.10.1.40\n  Mode: Aggressive (IKEv1)\n  PSK: Check backup share...\n" > /srv/samba/confidential/network_config.txt
RUN printf "FLAG{b2r_smb_hidden_share_a4c3}\n\nBackup notes:\n  - VPN PSK is reused as SSH password for user: ike (port 2222)\n  - Try: ssh ike@<target> -p 2222 with the PSK as password\n" > /srv/samba/backup/.backup_notes.txt
RUN printf "# IKE VPN Configuration\nike-vpn-psk = freakingrockstarontheroad\n# NOTE: This PSK is also used for SSH authentication\n" > /srv/samba/backup/vpn_config.bak

RUN chmod -R 777 /srv/samba/public
RUN chmod -R 750 /srv/samba/confidential
RUN chown -R smbadmin:smbadmin /srv/samba/confidential
RUN chmod -R 750 /srv/samba/backup
RUN chown -R smbadmin:smbadmin /srv/samba/backup

EXPOSE 139 445

CMD ["smbd", "--foreground", "--no-process-group"]
