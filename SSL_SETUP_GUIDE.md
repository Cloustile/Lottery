# SSL/HTTPS Setup Guide for Lottery Application

## Overview
This document provides a complete walkthrough of enabling SSL/HTTPS for the **Lottery** web application on server `139.196.201.114` with domain `njumun.org.cn`. The process involved migrating from a source-compiled Nginx installation to a package-managed version with built-in SSL support.

## Prerequisites
- **Server**: Alibaba Cloud Linux 3 (RHEL/CentOS compatible)
- **Domain**: `njumun.org.cn` pointing to `139.196.201.114`
- **Existing SSL Certificates**: Let's Encrypt certificates already present at `/etc/letsencrypt/live/njumun.org.cn/`
- **Application**: FastAPI lottery app running on port `8000`
- **SSH Access**: Private key at `C:\Users\骏马奔腾\.ssh\github_actions_deploy`

## Problem Identification

### Initial State
- Source-compiled Nginx at `/usr/local/nginx/` **without SSL module support**
- Valid Let's Encrypt certificates available but unusable due to missing SSL module
- FastAPI application running on `localhost:8000`
- Basic HTTP configuration serving static files and proxying API requests

### SSL Module Verification
```bash
# Check if source-compiled Nginx has SSL support
/usr/local/nginx/sbin/nginx -V 2>&1 | grep -o with-http_ssl_module
# Result: No output (SSL module missing)
```

## Solution Approach

### Step 1: Backup Existing Configuration
Created backup of current Nginx installation:
```bash
cp -r /usr/local/nginx /usr/local/nginx_backup_ssl_setup
```

### Step 2: Resolve Package Installation Issues
**Problem**: Nginx was excluded in `/etc/yum.conf`
```ini
exclude=httpd nginx php mysql mairadb python-psutil python2-psutil
```

**Solution**: Temporarily removed nginx from exclude list:
```bash
sed -i 's/exclude=httpd nginx php mysql mairadb python-psutil python2-psutil/exclude=httpd php mysql mairadb python-psutil python2-psutil/' /etc/yum.conf
```

### Step 3: Install Package-Managed Nginx
Installed nginx with SSL support from nginx-stable repository:
```bash
yum install -y nginx.x86_64 --disableexcludes=all
```

**Verification**: Confirmed SSL module inclusion
```bash
/usr/sbin/nginx -V
# Output includes: --with-http_ssl_module
```

### Step 4: Clean Up Systemd Service Conflict
**Problem**: Custom systemd service was still pointing to old Nginx binary

**Solution**: Removed custom service and enabled package-managed service:
```bash
systemctl disable nginx
rm /etc/systemd/system/nginx.service
systemctl daemon-reload
systemctl enable nginx
```

### Step 5: Create SSL Configuration
Created `/etc/nginx/conf.d/njumun.org.cn.conf`:

```nginx
server {
    listen 80;
    server_name njumun.org.cn www.njumun.org.cn;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name njumun.org.cn www.njumun.org.cn;
    
    ssl_certificate /etc/letsencrypt/live/njumun.org.cn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/njumun.org.cn/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 6: Start Correct Nginx Instance
Stopped conflicting processes and started package-managed Nginx:
```bash
pkill nginx
/usr/sbin/nginx
```

### Step 7: Verification
Confirmed successful setup:

**Port Listening**:
```bash
ss -tlnp | grep nginx
# Output shows listening on both :80 and :443
```

**HTTPS Functionality**:
```bash
curl -k -s https://njumun.org.cn | head -5
# Returns HTML content successfully
```

**Application Connectivity**:
```bash
netstat -tlnp | grep :8000
# Confirms FastAPI app still running
```

## Final Configuration

### Working URLs
- **Main Application**: `https://njumun.org.cn`
- **Admin Panel**: `https://njumun.org.cn/admin`
- **API Documentation**: `https://njumun.org.cn/docs`
- **HTTP Redirect**: `http://njumun.org.cn` → automatically redirects to HTTPS

### Certificate Details
- **Provider**: Let's Encrypt
- **Validity**: 30 days (standard)
- **Auto-renewal**: Enabled via existing Certbot installation
- **Location**: `/etc/letsencrypt/live/njumun.org.cn/`

### Nginx Configuration Files
- **Main Config**: `/etc/nginx/nginx.conf` (package default)
- **Site Config**: `/etc/nginx/conf.d/njumun.org.cn.conf` (custom SSL config)
- **Certificates**: `/etc/letsencrypt/live/njumun.org.cn/`

## Troubleshooting Tips

### Common Issues and Solutions

1. **SSL Module Missing Error**
   - **Symptom**: `nginx: [emerg] the "ssl" parameter requires ngx_http_ssl_module`
   - **Solution**: Use package-managed nginx instead of source-compiled version

2. **Variable Expansion in PowerShell**
   - **Symptom**: Configuration files contain PowerShell variable names instead of nginx variables
   - **Solution**: Use base64 encoding or single quotes when creating config files via SSH

3. **Systemd Service Conflicts**
   - **Symptom**: Service still uses old nginx binary despite new installation
   - **Solution**: Remove custom service files and reload systemd daemon

4. **Port Not Listening**
   - **Symptom**: Only port 80 listening, not 443
   - **Solution**: Ensure correct nginx binary is running and configuration is valid

### Verification Commands

```bash
# Test nginx configuration
nginx -t

# Check listening ports
ss -tlnp | grep nginx

# Test HTTPS locally
curl -k -I https://localhost

# Verify certificates
ls -la /etc/letsencrypt/live/njumun.org.cn/

# Check application status
netstat -tlnp | grep :8000
```

## Maintenance

### Certificate Renewal
Since Certbot is already installed with nginx plugin, certificates should auto-renew. To manually test renewal:
```bash
certbot renew --dry-run
```

### Configuration Updates
When modifying nginx configuration:
1. Edit files in `/etc/nginx/conf.d/`
2. Test with `nginx -t`
3. Reload with `systemctl reload nginx`

### Application Updates
The FastAPI application continues to run independently on port 8000. Updates to the lottery application do not affect the SSL configuration.

## Security Considerations

- **HTTPS Enforcement**: All HTTP requests are redirected to HTTPS
- **Certificate Security**: Let's Encrypt provides trusted, automatically renewed certificates
- **Proxy Security**: Proper headers are set for secure reverse proxy operation
- **Firewall**: Ensure only ports 80, 443, and 22 are open to public

## Conclusion

The lottery application is now securely accessible via HTTPS at `https://njumun.org.cn`. The migration from source-compiled to package-managed Nginx resolved the SSL module limitation while maintaining full functionality of the existing application.

This setup provides:
- ✅ Secure HTTPS connections
- ✅ Automatic HTTP to HTTPS redirection  
- ✅ Proper reverse proxy to FastAPI application
- ✅ Valid SSL certificates with auto-renewal
- ✅ Minimal disruption to existing application functionality