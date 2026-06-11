# Bot2Root CTF — Required Tools

This document lists all tools needed to solve the CTF, organized by stage.

---

## Core Requirements

| Tool | Purpose | Install |
|------|---------|---------|
| **Docker Engine** ≥ 24.0 | Run the lab | [docs.docker.com/engine/install](https://docs.docker.com/engine/install/) |
| **Docker Compose** ≥ 2.20 | Orchestrate containers | Included with Docker Desktop |

---

## Attacking Tools

### Essential (Required for most stages)

| Tool | Purpose | Stage |
|------|---------|-------|
| `nmap` | Port scanning, service detection | 4, 5 |
| `curl` | HTTP requests, API interaction | 1, 3, 5d, 9 |
| `hydra` | FTP brute forcing | 5a |
| `smbclient` | SMB share enumeration | 5b, 5c |
| `sshpass` | SSH with password (non-interactive) | 6, 8 |
| `ssh` | SSH tunneling, pivoting | 6, 8, 10 |
| `ftp` | FTP client | 5a |

### Recommended (Makes life easier)

| Tool | Purpose | Stage |
|------|---------|-------|
| `proxychains4` | SOCKS proxy for pivoting | 8 |
| `jq` | JSON parsing | 9 |
| `netcat` / `nc` | Network debugging | All |
| `ike-scan` | IKE VPN enumeration | 5c |
| `gobuster` / `ffuf` | Directory brute forcing | 3, 5d |
| `burpsuite` | HTTP proxy + repeater | 1, 2, 3 |

### Optional (Advanced stages)

| Tool | Purpose | Stage |
|------|---------|-------|
| `sqlmap` | Automated SQL injection | 1 |
| `wfuzz` | Web fuzzing | 3 |
| `redis-cli` | Redis interaction | 9 |

---

## Quick Install (Debian/Ubuntu/Kali)

```bash
# Essential tools
sudo apt update && sudo apt install -y \
  nmap \
  hydra \
  smbclient \
  curl \
  netcat-openbsd \
  sshpass \
  proxychains4 \
  ftp \
  jq

# IKE scanning (optional)
sudo apt install -y ike-scan

# Web fuzzing (optional)
sudo apt install -y gobuster ffuf
```

## Quick Install (macOS — Homebrew)

```bash
brew install nmap hydra curl sshpass jq
# smbclient: brew install samba
# proxychains: brew install proxychains-ng
```

## Quick Install (Arch Linux)

```bash
sudo pacman -S nmap hydra smbclient curl openssh proxychains-ng jq
```

---

## Pre-Built Attack VMs (Recommended)

If you don't want to install tools individually, use a pre-configured VM:

- **[Kali Linux](https://www.kali.org/get-kali/)** — Has all tools pre-installed
- **[Parrot Security](https://parrotsec.org/)** — Lightweight alternative to Kali
- **[BlackArch](https://blackarch.org/)** — Arch-based, 2800+ tools

Install Docker inside the VM, clone this repo, and run `docker compose up -d --build`.

---

## Verifying Your Setup

After installing tools, verify everything works:

```bash
# Check Docker
docker --version        # Should be ≥ 24.0
docker compose version  # Should be ≥ 2.20

# Check attacking tools
nmap --version
hydra -h 2>&1 | head -1
smbclient --version
curl --version | head -1
sshpass -V
ssh -V
```
