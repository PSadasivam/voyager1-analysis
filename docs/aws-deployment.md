# AWS Deployment Guide

Deploy the Voyager 1 Deep Space Analysis web app to an EC2 instance with Nginx, Gunicorn, and HTTPS.

## Prerequisites

- AWS account with IAM user (not root) that has EC2 and VPC permissions
- AWS CLI installed and configured (`aws configure`)
- A registered domain (e.g. via GoDaddy)
- An SSH key pair for EC2 access

> **Security note**: Never commit AWS credentials, SSH keys, `.pem` files, or secrets to this repository. All sensitive values below use placeholders.

---

## 1. Create a Key Pair

```bash
aws ec2 create-key-pair \
  --key-name voyager1-deploy \
  --query "KeyMaterial" \
  --output text > voyager1-deploy.pem

chmod 400 voyager1-deploy.pem
```

Store the `.pem` file in a secure location outside the repository. **Do not commit it.**

---

## 2. Create a Security Group

```bash
# Get the default VPC ID
aws ec2 describe-vpcs \
  --filters "Name=isDefault,Values=true" \
  --query "Vpcs[0].VpcId" --output text

# Create the security group (use your VPC ID)
aws ec2 create-security-group \
  --group-name voyager1-sg \
  --description "Voyager 1 web app - SSH, HTTP, HTTPS only" \
  --vpc-id <VPC_ID>

# Allow SSH (restrict to your IP)
aws ec2 authorize-security-group-ingress \
  --group-id <SECURITY_GROUP_ID> \
  --protocol tcp --port 22 \
  --cidr <YOUR_IP>/32

# Allow HTTP
aws ec2 authorize-security-group-ingress \
  --group-id <SECURITY_GROUP_ID> \
  --protocol tcp --port 80 \
  --cidr 0.0.0.0/0

# Allow HTTPS
aws ec2 authorize-security-group-ingress \
  --group-id <SECURITY_GROUP_ID> \
  --protocol tcp --port 443 \
  --cidr 0.0.0.0/0
```

Replace `<OUR_IP>` with our public IP address. **Do not open port 22 to `0.0.0.0/0`.**

---

## 3. Launch an EC2 Instance

```bash
# Find the latest Amazon Linux 2023 AMI for your region
aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023*-x86_64" "Name=state,Values=available" \
  --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" \
  --output text

# Launch the instance
aws ec2 run-instances \
  --image-id <AMI_ID> \
  --instance-type t2.micro \
  --key-name voyager1-deploy \
  --security-group-ids <SECURITY_GROUP_ID> \
  --count 1 \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=voyager1-web}]"

# Wait for the instance to reach running state
aws ec2 wait instance-running --instance-ids <INSTANCE_ID>
```

> The AMI lookup above finds the latest Amazon Linux 2023 image. Adjust the `--filters` if using a different region or architecture.

---

## 4. Allocate and Associate an Elastic IP

```bash
# Allocate
aws ec2 allocate-address --domain vpc

# Note the AllocationId from the output, then associate
aws ec2 associate-address \
  --instance-id <INSTANCE_ID> \
  --allocation-id <ALLOCATION_ID>
```

Record the Elastic IP for DNS configuration later.

---

## 5. SSH into the Instance

```bash
ssh -i voyager1-deploy.pem ec2-user@<ELASTIC_IP>
```

---

## 6. Server Setup

Run the following on the EC2 instance:

```bash
# System updates (Amazon Linux 2023 uses dnf)
sudo dnf update -y

# Install Python 3.11, pip, Nginx, Git
sudo dnf install -y python3.11 python3.11-pip python3.11-devel nginx git

# Clone the repository
git clone https://github.com/PSadasivam/voyager1-analysis.git
cd voyager1-analysis

# Create virtual environment with Python 3.11 and install dependencies
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

> Python 3.11+ is required because the codebase uses modern type syntax (`list[str] | None`).

---

## 7. Configure Gunicorn as a systemd Service

Create `/etc/systemd/system/voyager1.service`:

```bash
sudo tee /etc/systemd/system/voyager1.service > /dev/null <<'EOF'
[Unit]
Description=Voyager1 Flask App (Gunicorn)
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/voyager1-analysis
ExecStart=/home/ec2-user/voyager1-analysis/venv/bin/gunicorn \
  --workers 2 \
  --bind 127.0.0.1:8000 \
  voyager1_web_app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable voyager1
sudo systemctl start voyager1
```

Verify it is running:

```bash
sudo systemctl status voyager1
curl http://127.0.0.1:8000
```

> Gunicorn binds to `127.0.0.1` only — it is **not** exposed to the internet directly. Nginx handles all external traffic.

---

## 8. Configure Nginx as a Reverse Proxy

Create `/etc/nginx/conf.d/voyager1.conf`:

```bash
sudo tee /etc/nginx/conf.d/voyager1.conf > /dev/null <<'EOF'
server {
    listen 80;
    server_name <YOUR_DOMAIN> www.<YOUR_DOMAIN>;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;

    # Block dotfiles (e.g. .env, .git)
    location ~ /\. {
        deny all;
        return 404;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo nginx -t
sudo systemctl enable nginx
sudo systemctl start nginx
```

Replace `<YOUR_DOMAIN>` with your actual domain (e.g. `prabhusadasivam.com`).

> Certbot will automatically modify this file to add the HTTPS server block and HTTP-to-HTTPS redirect when you run it in the next step.

---

## 9. Enable HTTPS with Let's Encrypt

```bash
# Install Certbot
sudo dnf install -y certbot python3-certbot-nginx

# Obtain certificate for bare domain first
sudo certbot --nginx \
  -d <YOUR_DOMAIN> \
  --non-interactive \
  --agree-tos \
  --redirect \
  -m <YOUR_EMAIL>

# Expand certificate to include www
sudo certbot --nginx \
  -d <YOUR_DOMAIN> \
  -d www.<YOUR_DOMAIN> \
  --non-interactive \
  --agree-tos \
  --redirect \
  --expand \
  -m <YOUR_EMAIL>

# Verify auto-renewal
sudo certbot renew --dry-run
```

Certbot automatically configures Nginx to redirect HTTP to HTTPS and sets up a systemd timer for certificate renewal.

> If certbot fails for `www` on the first attempt (e.g. due to DNS propagation delay), obtain the bare domain cert first, then expand it to include `www` once DNS is fully resolved.

---

## 10. Connect Your GoDaddy Domain

In GoDaddy DNS Management for your domain:

| Type  | Name  | Value              | TTL    |
|-------|-------|--------------------|--------|
| A     | @     | `<ELASTIC_IP>`     | 600    |
| CNAME | www   | `<YOUR_DOMAIN>`    | 1 Hour |

DNS propagation can take up to 48 hours.

---

## Security Checklist

- [ ] IAM user with least-privilege policy (not root account)
- [ ] SSH key stored securely, never committed to the repo
- [ ] SSH access restricted to your IP only (port 22)
- [ ] Gunicorn bound to `127.0.0.1` (not `0.0.0.0`)
- [ ] Flask `debug=True` disabled in production (set `debug=False` or use Gunicorn)
- [ ] Nginx security headers configured (X-Frame-Options, CSP, etc.)
- [ ] Dotfiles blocked by Nginx (`.env`, `.git`)
- [ ] HTTPS enabled with auto-renewing Let's Encrypt certificate
- [ ] No secrets, credentials, or `.pem` files in the repository
- [ ] OS packages kept up to date (`sudo dnf update -y`)
- [ ] Flask `SECRET_KEY` set via environment variable, not hardcoded

---

## Updating the Application

```bash
ssh -i voyager1-deploy.pem ec2-user@<ELASTIC_IP>
cd voyager1-analysis
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart voyager1
```

---

## Teardown

To remove all AWS resources when no longer needed:

```bash
# Stop and terminate the instance
aws ec2 terminate-instances --instance-ids <INSTANCE_ID>

# Release the Elastic IP
aws ec2 release-address --allocation-id <ALLOCATION_ID>

# Delete the security group (after instance is terminated)
aws ec2 delete-security-group --group-id <SECURITY_GROUP_ID>

# Delete the key pair
aws ec2 delete-key-pair --key-name voyager1-deploy
```

Delete the local `.pem` file as well.
