# InnerPieces - Digital Ocean Deployment Guide

## Prerequisites
- Digital Ocean account
- Domain name (optional but recommended)
- Git repository with your code

---

## Option 1: Deploy to App Platform (Recommended - Easiest)

### Step 1: Push your code to GitHub
```bash
git add -A
git commit -m "Prepare for Digital Ocean deployment"
git push origin master
```

### Step 2: Create App on Digital Ocean
1. Go to [Digital Ocean App Platform](https://cloud.digitalocean.com/apps)
2. Click **Create App**
3. Connect your GitHub repository
4. Select the `innerpieces` repository and `master` branch

### Step 3: Configure Environment Variables
Add these environment variables in the App Platform settings:
| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `your-app-name.ondigitalocean.app` |
| `DATABASE_URL` | Auto-configured if using managed database |

### Step 4: Configure Build & Run Commands
- **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Run Command:** `gunicorn innerpieces.wsgi:application --config gunicorn.conf.py`

### Step 5: Add a Database (Optional)
1. In your app settings, click **Add Resource**
2. Select **Database** → **PostgreSQL**
3. The `DATABASE_URL` will be auto-configured

---

## Option 2: Deploy to a Droplet (More Control)

### Step 1: Create a Droplet
1. Go to [Digital Ocean Droplets](https://cloud.digitalocean.com/droplets)
2. Create a new Droplet:
   - **Image:** Ubuntu 22.04 LTS
   - **Size:** Basic, $6/month (1GB RAM) minimum
   - **Authentication:** SSH keys (recommended)

### Step 2: Initial Server Setup
```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install required packages
apt install python3-pip python3-venv nginx postgresql postgresql-contrib -y

# Create a non-root user
adduser innerpieces
usermod -aG sudo innerpieces
su - innerpieces
```

### Step 3: Clone and Setup Project
```bash
# Clone your repository
cd /home/innerpieces
git clone https://github.com/Dominic62q/InnerPieces.git app
cd app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Create .env file
cp .env.example .env
nano .env
```

Update `.env` with your production values:
```
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-droplet-ip
DATABASE_URL=postgres://user:password@localhost:5432/innerpieces
```

### Step 5: Setup PostgreSQL Database
```bash
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE innerpieces;
CREATE USER innerpieces_user WITH PASSWORD 'your-secure-password';
ALTER ROLE innerpieces_user SET client_encoding TO 'utf8';
ALTER ROLE innerpieces_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE innerpieces_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE innerpieces TO innerpieces_user;
\q
```

### Step 6: Run Migrations & Collect Static
```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### Step 7: Setup Gunicorn Service
```bash
sudo nano /etc/systemd/system/innerpieces.service
```

Add this content:
```ini
[Unit]
Description=InnerPieces Gunicorn Daemon
After=network.target

[Service]
User=innerpieces
Group=www-data
WorkingDirectory=/home/innerpieces/app
ExecStart=/home/innerpieces/app/venv/bin/gunicorn innerpieces.wsgi:application --config gunicorn.conf.py

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl start innerpieces
sudo systemctl enable innerpieces
sudo systemctl status innerpieces
```

### Step 8: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/innerpieces
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com your-droplet-ip;

    location /static/ {
        alias /home/innerpieces/app/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/innerpieces /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 9: Setup SSL with Let's Encrypt (Optional but Recommended)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Useful Commands

### Check Service Status
```bash
sudo systemctl status innerpieces
sudo systemctl status nginx
```

### View Logs
```bash
sudo journalctl -u innerpieces -f
```

### Restart Services
```bash
sudo systemctl restart innerpieces
sudo systemctl restart nginx
```

### Update Deployment
```bash
cd /home/innerpieces/app
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart innerpieces
```

---

## Generate Secret Key
Run this command locally to generate a new secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
