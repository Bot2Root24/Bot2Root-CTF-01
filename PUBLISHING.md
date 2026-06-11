# Docker Hub Publishing Guide

## Prerequisites

1. Create a Docker Hub account at [hub.docker.com](https://hub.docker.com)
2. Login from the command line:
   ```bash
   docker login
   # Enter your Docker Hub username and password/token
   ```

---

## Option A: Publish as GitHub Repository (Recommended)

Users clone the repo and build locally. This is the simplest and most transparent approach.

### Steps

1. **Create a GitHub repository**:
   ```bash
   cd /home/ubuntu/bot2root-ctf-public
   git init
   git add .
   git commit -m "Initial release: Bot2Root CTF v1.0"
   git branch -M main
   git remote add origin https://github.com/bot2root/bot2root-ctf.git
   git push -u origin main
   ```

2. **Users run**:
   ```bash
   git clone https://github.com/bot2root/bot2root-ctf.git
   cd bot2root-ctf
   docker compose up -d --build
   ```

---

## Option B: Push Pre-Built Images to Docker Hub

Users pull pre-built images — faster setup, no build required.

### Step 1: Build All Images Locally

```bash
cd /home/ubuntu/bot2root-ctf-public
docker compose build
```

### Step 2: Tag Images for Docker Hub

```bash
# Replace 'bot2root' with your Docker Hub username
DHUB=bot2root

docker tag bot2root-ctf-public-lab01-web:latest    $DHUB/b2r-web:latest
docker tag bot2root-ctf-public-lab01-ftp:latest    $DHUB/b2r-ftp:latest
docker tag bot2root-ctf-public-lab01-smb:latest    $DHUB/b2r-smb:latest
docker tag bot2root-ctf-public-lab01-ike:latest    $DHUB/b2r-ike:latest
docker tag bot2root-ctf-public-lab01-nginx:latest  $DHUB/b2r-nginx:latest
docker tag bot2root-ctf-public-lab01-gateway:latest $DHUB/b2r-gateway:latest
docker tag bot2root-ctf-public-lab02-api:latest    $DHUB/b2r-api:latest
docker tag bot2root-ctf-public-lab02-ssh:latest    $DHUB/b2r-ssh:latest
docker tag bot2root-ctf-public-lab02-java:latest   $DHUB/b2r-java:latest
docker tag bot2root-ctf-public-lab02-metadata:latest $DHUB/b2r-metadata:latest
# redis uses the official image — no need to push
```

### Step 3: Push to Docker Hub

```bash
DHUB=bot2root

for img in b2r-web b2r-ftp b2r-smb b2r-ike b2r-nginx b2r-gateway b2r-api b2r-ssh b2r-java b2r-metadata; do
  echo "Pushing $DHUB/$img..."
  docker push $DHUB/$img:latest
done
```

### Step 4: Create a Pre-Built docker-compose.yml

Create a `docker-compose.hub.yml` that references Docker Hub images instead of local builds:

```yaml
# Replace all 'build:' sections with 'image:' sections
# Example:
services:
  lab01-web:
    image: bot2root/b2r-web:latest
    # ... (rest of config stays the same, minus 'build:')
```

### Step 5: Users Run

```bash
# Download the compose file
curl -O https://raw.githubusercontent.com/bot2root/bot2root-ctf/main/docker-compose.hub.yml

# Start with pre-built images (no build required)
docker compose -f docker-compose.hub.yml up -d
```

---

## Option C: Single Downloadable Archive

Package everything as a `.tar.gz` for users without Git.

```bash
cd /home/ubuntu
tar czf bot2root-ctf-v1.0.tar.gz \
  --exclude='.git' \
  bot2root-ctf-public/

# Upload to GitHub Releases, Google Drive, or any file host
# Users download, extract, and run:
#   tar xzf bot2root-ctf-v1.0.tar.gz
#   cd bot2root-ctf-public
#   docker compose up -d --build
```

---

## Multi-Architecture Builds (Optional)

To support both AMD64 and ARM64 (Apple Silicon):

```bash
# Create a builder
docker buildx create --name b2r-builder --use

# Build and push multi-arch images
DHUB=bot2root
for svc in lab01-web lab01-ftp lab01-smb lab01-ike lab01-nginx lab01-gateway lab02-api lab02-ssh lab02-java lab02-metadata; do
  SHORT=$(echo $svc | sed 's/lab0[12]-/b2r-/')
  CONTEXT=$(echo $svc | sed 's/-/\//' | sed 's/lab0/lab0/')
  # Determine context path
  case $svc in
    lab01-*) CTX="./lab01/$(echo $svc | sed 's/lab01-//')" ;;
    lab02-*) CTX="./lab02/$(echo $svc | sed 's/lab02-//')" ;;
  esac
  
  echo "Building $DHUB/$SHORT from $CTX..."
  docker buildx build --platform linux/amd64,linux/arm64 \
    -t $DHUB/$SHORT:latest --push "$CTX"
done
```

---

## Verification

After pushing, verify images are accessible:

```bash
# Check image exists on Docker Hub
docker pull bot2root/b2r-web:latest
docker inspect bot2root/b2r-web:latest | jq '.[0].Architecture'
```

Visit `https://hub.docker.com/u/bot2root` to see all your repositories.
