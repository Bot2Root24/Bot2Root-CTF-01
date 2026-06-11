# Bot2Root CTF

A multi-stage penetration testing Capture The Flag (CTF) lab featuring **11 Docker containers** across **3 segmented networks**. Designed for security professionals and students to practice real-world web, network, and privilege escalation attacks in a safe, local environment.

![Docker](https://img.shields.io/badge/Docker-Required-blue?logo=docker)
![Difficulty](https://img.shields.io/badge/Difficulty-Intermediate--Advanced-orange)
![Flags](https://img.shields.io/badge/Flags-15+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Overview

Bot2Root simulates a realistic corporate network with multiple attack surfaces. You'll chain vulnerabilities across web applications, network services, and Linux systems to capture **15+ flags** through **10 stages** of increasing difficulty.

### Attack Stages

| Stage | Category | Technique |
|-------|----------|-----------|
| 1 | Web | SQLi with WAF bypass + Rate limit evasion |
| 2 | Web | Stored DOM-based XSS |
| 3 | Web | File upload → Rename → Remote Code Execution |
| 4 | Network | Port scanning & service enumeration |
| 5 | Network | FTP brute force, SMB enumeration, Nginx 401 bypass |
| 6 | Network | SSH access via VPN PSK password reuse |
| 7 | Privesc | SUID binary exploitation + Cron job abuse |
| 8 | Pivoting | SSH local port forwarding through gateway |
| 9 | Web/Cloud | SSRF chain → credential leak + metadata exposure |
| 10 | Privesc | LOLBin (nmap GTFOBins) root escalation |

### Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      YOUR MACHINE                           │
│               (Kali / Parrot / Any Linux)                   │
└──────────┬──────────────────────────────────────────────────┘
           │  Exposed: 80, 8080, 21, 445, 139, 2222, 500/udp
           ▼
┌───────────── lab01-net (10.10.1.0/24) ─────────────────────┐
│  Web App     10.10.1.10   (Flask, port 80)                 │
│  FTP Server  10.10.1.20   (vsftpd, port 21)               │
│  SMB Server  10.10.1.30   (Samba, port 445)                │
│  IKE/SSH     10.10.1.40   (StrongSwan + SSH, port 2222)    │
│  Nginx       10.10.1.50   (Nginx, port 8080)              │
│  Gateway     10.10.1.254  (dual-homed router)              │
└──────────────────┬─────────────────────────────────────────┘
                   │  SSH tunnel required
                   ▼
┌───────────── lab02-net (10.10.2.0/24) ─────────────────────┐
│  API Server  10.10.2.10   (SSRF-vulnerable Flask API)      │
│  SSH Target  10.10.2.40   (LOLBin privilege escalation)    │
│  Gateway     10.10.2.254  (dual-homed router)              │
└──────────────────┬─────────────────────────────────────────┘
                   │  SSRF only — no direct access
                   ▼
┌───────────── lab03-net (10.10.3.0/24) ─────────────────────┐
│  ★ INTERNAL ONLY — reachable via SSRF chain only           │
│  Metadata    10.10.3.50   (simulated AWS IMDS)             │
│  Redis       10.10.3.30   (no authentication)              │
│  Java App    10.10.3.20   (Tomcat)                         │
└────────────────────────────────────────────────────────────┘
```

---

## Requirements

### System
- **Docker Engine** ≥ 24.0
- **Docker Compose** ≥ 2.20 (included with Docker Desktop)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk**: ~3 GB for images
- **OS**: Linux, macOS, or Windows (with WSL2)

### Attacking Tools (on your host machine)

Install these tools to solve the CTF. A Kali/Parrot VM has most of them pre-installed.

```bash
# Debian/Ubuntu/Kali
sudo apt update && sudo apt install -y \
  nmap hydra smbclient curl netcat-openbsd \
  sshpass proxychains4 ftp jq

# Optional (for IKE scanning)
sudo apt install -y ike-scan strongswan-starter
```

See [REQUIREMENTS.md](REQUIREMENTS.md) for detailed tool descriptions and alternative installation methods.

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/bot2root/bot2root-ctf.git
cd bot2root-ctf
```

### 2. Start the Lab
```bash
docker compose up -d --build
```

First build takes **3–5 minutes** (downloads base images + compiles SUID binary). Subsequent starts are instant.

### 3. Verify All Containers Are Running
```bash
docker compose ps
```

You should see **11 containers** all with status `Up`:
```
NAME             STATUS
lab01-web        Up
lab01-ftp        Up
lab01-smb        Up
lab01-ike        Up
lab01-nginx      Up
lab01-gateway    Up
lab02-api        Up
lab02-ssh        Up
lab02-java       Up
lab02-redis      Up
lab02-metadata   Up
```

### 4. Access the Web App
Open your browser: **http://localhost**

You'll see the Bot2Root login page. Your first challenge starts here.

### 5. Start Scanning
```bash
# TCP port scan
sudo nmap -Pn -sV localhost -p 21,80,139,445,2222,8080

# UDP scan for IKE
sudo nmap -Pn -sU localhost -p 500,4500
```

---

## Port Mapping

| Host Port | Container | Service |
|-----------|-----------|---------|
| 80 | lab01-web | Flask web application |
| 8080 | lab01-nginx | Nginx (info disclosure) |
| 21 | lab01-ftp | FTP server (vsftpd) |
| 139, 445 | lab01-smb | SMB file shares (Samba) |
| 2222 | lab01-ike | SSH + IKE VPN (StrongSwan) |
| 500/udp | lab01-ike | IKE VPN |
| 4500/udp | lab01-ike | IKE NAT-T |

> **Lab02 and Lab03** containers have no exposed ports — you must pivot through the gateway to reach them.

---

## Flag Format

```
FLAG{b2r_description_xxxx}
```

There are **15+ flags** hidden across all stages. Document each flag as you find it.

---

## Hints

<details>
<summary>Stage 1 — Where to start?</summary>

Try logging into the web app at `http://localhost`. The login form has a SQL injection vulnerability, but there's a WAF. Also watch for rate limiting — can you bypass it?

</details>

<details>
<summary>Stage 5 — What services are running?</summary>

Scan all ports. FTP has a banner that leaks a username. SMB has multiple shares — some hidden. The Nginx server has a protected path that can be bypassed with the right header.

</details>

<details>
<summary>Stage 7 — How to escalate on IKE?</summary>

Look for SUID binaries (`find / -perm -4000 -type f 2>/dev/null`) and cron jobs (`cat /etc/cron.d/*`). There are two separate privilege escalation paths.

</details>

<details>
<summary>Stage 9 — How to reach internal services?</summary>

The API server has an SSRF vulnerability at `/api/fetch`. Some endpoints are restricted to localhost — can you make the server request itself? The API is also connected to an internal network with a metadata service.

</details>

---

## Management

### Stop the Lab
```bash
docker compose down
```

### Full Reset (clear all data)
```bash
docker compose down -v
docker compose up -d --build
```

### View Logs
```bash
# All containers
docker compose logs -f

# Specific container
docker compose logs -f lab01-web
```

### Shell into a Container (for debugging)
```bash
docker exec -it lab01-web /bin/bash
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 80 already in use | Stop Apache/Nginx: `sudo systemctl stop apache2 nginx` or change port in `docker-compose.yml` |
| Port 445 already in use | Stop local Samba: `sudo systemctl stop smbd` |
| Containers won't start | Check Docker is running: `docker info` |
| Can't scan UDP ports | Use `sudo nmap` (raw sockets need root) |
| FTP passive mode fails | Ensure ports 30000-30009 are not blocked by firewall |
| nmap `-sC` crashes | Known bug in nmap 7.98 snap package. Use `apt install nmap` instead |
| Build fails on ARM Mac | Add `platform: linux/amd64` to services in `docker-compose.yml` |

---

## Credits

Created by **Raghuveer Chouhan** ([@rveer](https://github.com/bot2root))

Built for security training and education. Use responsibly.

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

**Disclaimer**: This CTF lab is for authorized educational use only. Do not use the techniques learned here against systems without explicit permission.
