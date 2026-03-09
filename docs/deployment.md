# Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Server Setup](#server-setup)
4. [Initial Deployment](#initial-deployment)
5. [GitHub Actions Setup](#github-actions-setup)
6. [Domain Configuration](#domain-configuration)
7. [SSL/HTTPS](#sslhttps)
8. [Maintenance](#maintenance)
9. [Monitoring](#monitoring)
10. [Backup](#backup)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers deploying the ADA Bali Events platform to a DigitalOcean droplet using Docker and GitHub Actions.

### Architecture

```
┌─────────────────────────────┐
│      Internet               │
│         ↓                   │
│    DigitalOcean             │
│    ┌─────────────────┐      │
│    │   Nginx (80/443)│      │
│    └────────┬────────┘      │
│              ↓               │
│    ┌─────────────────┐      │
│    │ Django + Gunicorn│     │
│    └────────┬────────┘      │
│              ↓               │
│    ┌─────────────────┐      │
│    │  PostgreSQL     │      │
│    └─────────────────┘      │
└─────────────────────────────┘
```

### Cost Estimate

| Resource | Cost |
|----------|------|
| DigitalOcean Droplet (1GB RAM) | $10/month |
| Domain | ~$10/year |
| **Total** | ~$10-12/month |

---

## Prerequisites

### Local Machine

- Git installed
- GitHub account
- SSH key generated

### Server

- DigitalOcean account
- Ubuntu 22.04 LTS droplet
- Domain (optional but recommended)

---

## Server Setup

### 1. Create DigitalOcean Droplet

1. Log in to [DigitalOcean](https://digitalocean.com)
2. Click "Create" → "Droplets"
3. Choose:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: $10/month (1GB RAM, 25GB SSD)
   - **Region**: Singapore (closest to Bali)
   - **Authentication**: SSH keys (recommended)
4. Note your droplet IP address

### 2. Connect to Server

```bash
ssh root@your-droplet-ip
```

### 3. Install Docker

```bash
# Update package list
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Enable Docker
systemctl start docker
systemctl enable docker

# Add user to docker group (optional)
usermod -aG docker $USER
```

### 4. Install Docker Compose

```bash
apt install docker-compose -y
```

### 5. Configure Firewall

```bash
# Allow SSH
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable
```

---

## Initial Deployment

### 1. Create Project Directory

```bash
mkdir -p /home/jmx/ada-events
cd /home/jmx/ada-events
```

### 2. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ada-events.git .
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Edit `.env` with your settings:

```bash
# Required
SECRET_KEY=generate-a-secure-random-key-here
POSTGRES_PASSWORD=create-secure-password

# Optional (use defaults)
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-droplet-ip
POSTGRES_DB=ada_events
POSTGRES_USER=postgres
```

Recommended production hardening:

```bash
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

Generate a secure secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Build and Start Containers

```bash
docker-compose up -d --build
```

This will:
- Build the Django application
- Start PostgreSQL database
- Start Nginx reverse proxy

### 5. Verify Containers are Running

```bash
docker-compose ps
```

Expected output:
```
      Name                   Command               State          Ports
-------------------------------------------------------------------------
ada-events_db_1      docker-entrypoint.sh postgres    Up      5432/tcp
ada-events_nginx_1   /docker-entrypoint.sh ngin ...   Up      0.0.0.0:80->80/tcp
ada-events_web_1     gunicorn --bind 0.0.0.0:8 ...   Up
```

### 6. Run Migrations

```bash
docker-compose exec -T web python manage.py migrate
```

### 7. Create Superuser

```bash
docker-compose exec -T web python manage.py createsuperuser
```

### 8. Access the Application

- Open http://your-droplet-ip:8080 (or your domain through reverse proxy)
- Admin panel: http://your-droplet-ip:8080/admin

---

## GitHub Actions Setup

### 1. Generate SSH Key for Deployments

On your local machine:

```bash
# Generate deploy key (no passphrase)
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions

# Display public key
cat ~/.ssh/github_actions.pub
```

### 2. Add Deploy Key to Server

On your droplet:

```bash
# Add public key to authorized_keys
echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys

# Test connection
ssh -i ~/.ssh/github_actions root@your-droplet-ip
```

### 3. Add GitHub Secrets

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:

| Secret | Value |
|--------|-------|
| `DO_HOST` | Your droplet IP address |
| `DO_USERNAME` | `root` |
| `DO_SSH_KEY` | Private key from `~/.ssh/github_actions` |

### 4. Test the Pipeline

Push to main branch:

```bash
git add .
git commit -m "feat: test deployment"
git push origin main
```

Check GitHub Actions tab to see progress. If successful, your site is live!

---

## Domain Configuration

### 1. Point Domain to Droplet

In your domain registrar:

- Add **A Record** pointing to your droplet IP
- Example: `events.adabali.com → 123.456.789.0`

### 2. Update ALLOWED_HOSTS

Edit `.env` on your droplet:

```bash
ALLOWED_HOSTS=your-domain.com,your-droplet-ip,localhost
```

### 3. Rebuild

```bash
docker-compose exec -T web python manage.py migrate
docker-compose restart web
```

---

## SSL/HTTPS

### Using Certbot (Recommended)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Generate SSL certificate
certbot --nginx -d your-domain.com

# Follow prompts
# Choose "Redirect" to force HTTPS
```

### Auto-Renewal

Certbot sets up auto-renewal by default. Verify:

```bash
certbot renew --dry-run
```

---

## Maintenance

### Updating the Application

Simply push to main branch - GitHub Actions handles deployment automatically.

### Event Reminders Cron

Run reminder generation every 15 minutes:

```bash
*/15 * * * * cd /home/jmx/ada-events && docker compose exec -T web python manage.py send_event_reminders --hours-ahead 24 >> /var/log/ada-events-reminders.log 2>&1
```

Test first:

```bash
docker compose exec -T web python manage.py send_event_reminders --dry-run
```

### Seed Categories (First Deploy)

```bash
docker compose exec -T web python manage.py seed_categories
```

### Manual Update (Emergency)

```bash
cd /home/jmx/ada-events
git pull origin main
docker-compose up -d --build
docker-compose exec -T web python manage.py migrate
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db
```

### Restarting Services

```bash
# Restart all
docker-compose restart

# Restart specific
docker-compose restart web
```

---

## Monitoring

### Check System Resources

```bash
# Docker stats
docker stats

# System resources
htop

# Disk usage
df -h
```

### Check Application Health

```bash
# Check if responding
curl -I http://localhost

# Check logs
docker-compose logs web --tail=50
```

---

## Backup

### Database Backup

```bash
# Create backup
docker-compose exec -T db pg_dump -U postgres ada_events > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T db psql -U postgres ada_events < backup_20260101.sql
```

### Automated Backups (Optional)

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * docker-compose -f /home/jmx/ada-events/docker-compose.yml exec -T db pg_dump -U postgres ada_events > /home/jmx/backups/ada_events_$(date +\%Y\%m\%d).sql
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Common issues:
# - Port 80 in use: docker-compose down && docker-compose up -d
# - Database not ready: wait a few seconds then retry
```

### Database Connection Error

```bash
# Check if database container is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify connection
docker-compose exec web python manage.py dbshell
```

### Static Files Not Loading

```bash
# Collect static files
docker-compose exec -T web python manage.py collectstatic

# Check nginx config
docker-compose exec nginx nginx -t
```

### 502 Bad Gateway

```bash
# Check web container
docker-compose logs web

# Restart services
docker-compose restart
```

### Out of Memory

Check droplet resources - 1GB RAM may be tight. Consider:

1. Add swap
2. Reduce Gunicorn workers
3. Upgrade to 2GB RAM droplet

---

## Rollback

If deployment fails:

```bash
# Check previous version
git log

# Revert to previous commit
git revert HEAD
git push origin main
```

Or manually revert:

```bash
# SSH to server
cd /home/jmx/ada-events

# Check git log
git log --oneline

# Revert
git revert COMMIT_HASH

# Rebuild
docker-compose up -d --build
```
