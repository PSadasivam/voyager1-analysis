# Ticket: Deploy Voyager 1 Web App to AWS EC2

## Summary

Provision an AWS EC2 instance and deploy the Voyager 1 Flask web application, fronted by Nginx and Gunicorn, with HTTPS via Let's Encrypt. Connect the GoDaddy domain (PrabhuSadasivam.com) to the instance.

## Reference

See [docs/aws-deployment.md](aws-deployment.md) for the full step-by-step runbook.

---

## Acceptance Criteria

- [ ] Site is accessible at `https://prabhusadasivam.com`
- [ ] HTTP redirects to HTTPS
- [ ] All dashboard pages load (Home, Facts, Trajectory, Plasma, Density, Magnetometer)
- [ ] SSH access restricted to operator IP only
- [ ] No secrets, keys, or credentials committed to the repository
- [ ] Flask debug mode disabled in production
- [ ] Gunicorn bound to localhost; only Nginx exposed to the internet
- [ ] Let's Encrypt certificate installed with auto-renewal verified

---

## Tasks

### 1. AWS Infrastructure Setup
- [ ] Create IAM user with least-privilege EC2/VPC policy
- [ ] Generate SSH key pair (`voyager1-deploy`), store `.pem` securely outside repo
- [ ] Create security group (`voyager1-sg`): ports 22 (operator IP only), 80, 443
- [ ] Launch `t2.micro` EC2 instance (Amazon Linux 2)
- [ ] Allocate and associate an Elastic IP

### 2. Server Provisioning
- [ ] SSH into instance and run system updates
- [ ] Install Python 3, pip, Nginx, Git
- [ ] Clone `PSadasivam/voyager1-analysis` from GitHub
- [ ] Create virtual environment and install `requirements.txt` + `gunicorn`

### 3. Application Deployment
- [ ] Create systemd service (`voyager1.service`) running Gunicorn on `127.0.0.1:8000`
- [ ] Configure Nginx reverse proxy with security headers
- [ ] Block dotfile access (`.env`, `.git`) in Nginx config
- [ ] Verify site loads on `http://<ELASTIC_IP>`

### 4. HTTPS and Domain
- [ ] Install Certbot and obtain Let's Encrypt certificate
- [ ] Verify HTTP-to-HTTPS redirect
- [ ] Confirm `certbot renew --dry-run` succeeds
- [ ] In GoDaddy DNS: set A record `@` → Elastic IP, CNAME `www` → domain
- [ ] Wait for DNS propagation and verify `https://prabhusadasivam.com`

### 5. Production Hardening
- [ ] Set Flask `SECRET_KEY` via environment variable (not hardcoded)
- [ ] Ensure `debug=False` in production (Gunicorn does not use Flask dev server)
- [ ] Enable `client_max_body_size` limit in Nginx
- [ ] Verify security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)

### 6. Validation
- [ ] Smoke-test all routes: `/`, `/facts`, `/trajectory`, `/plasma`, `/density`, `/dashboard`
- [ ] Confirm Gunicorn restarts automatically on crash (`Restart=always`)
- [ ] Confirm Nginx and Gunicorn start on boot (`systemctl enable`)
- [ ] Run `nmap` or security group audit to confirm only ports 22, 80, 443 are open

---

## Estimated Cost

| Resource             | Cost                          |
|----------------------|-------------------------------|
| EC2 t2.micro         | Free tier (1 year), ~$8/mo after |
| Elastic IP           | Free while attached to running instance |
| Let's Encrypt SSL    | Free                          |
| GoDaddy domain       | Existing (no additional cost) |

---

## Rollback / Teardown

If the deployment needs to be reverted, follow the **Teardown** section in [docs/aws-deployment.md](aws-deployment.md) to terminate the instance, release the Elastic IP, and clean up the security group and key pair.
