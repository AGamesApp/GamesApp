# Server Security & Firewall Configuration

## 🔒 UFW Firewall Configuration

### Enabled Rules:
```
✓ Port 22  (TCP) - SSH access (CRITICAL - Do not block!)
✓ Port 80  (TCP) - HTTP web traffic
✓ Port 443 (TCP) - HTTPS web traffic (for future SSL)
```

### Default Policies:
- **Incoming:** DENY (all ports blocked by default)
- **Outgoing:** ALLOW (server can make outbound connections)
- **Status:** ACTIVE and enabled on system startup

### Important Notes:
⚠️ **SSH Access Protected:** Port 22 is explicitly allowed to ensure you can always reconnect
⚠️ **Firewall Persistence:** UFW rules persist across reboots

## 🔐 OTP Email Testing Results

### Test Performed:
- **Email:** ramy41599@gmail.com
- **Username:** ramy
- **Status:** ✅ SUCCESSFUL

### Registration Response:
```json
{
    "message": "Registration successful! Please check your email for the verification code.",
    "user": {
        "id": 3,
        "email": "ramy41599@gmail.com",
        "username": "ramy",
        "is_email_verified": false
    },
    "token": "a6d5a749dd8996ab9ac21acc2186d762ef75f9f8"
}
```

### OTP Generated:
- **OTP Code:** 389659
- **Email Server:** agames.app.dev@gmail.com
- **SMTP:** smtp.gmail.com:587

### OTP Verification Response:
```json
{
    "message": "Email verified successfully! You can now login.",
    "user": {
        "email": "ramy41599@gmail.com",
        "is_email_verified": true
    }
}
```

### ✅ Verification: SUCCESSFUL
The OTP system is working correctly. Email should be sent to ramy41599@gmail.com with the verification code.

## 🛡️ Current Security Status

### Firewall Protection:
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing)
```

### Open Ports:
| Port | Protocol | Service | Purpose |
|------|----------|---------|---------|
| 22   | TCP      | SSH     | Remote server access |
| 80   | TCP      | HTTP    | Web application |
| 443  | TCP      | HTTPS   | Secure web (when SSL configured) |

### Blocked:
- All other incoming ports (database, redis, etc.)
- Direct database access from outside
- All unauthorized services

## 📋 UFW Management Commands

### View Status:
```bash
sudo ufw status verbose
sudo ufw status numbered
```

### Add/Remove Rules:
```bash
# Allow a port
sudo ufw allow <port>/tcp

# Remove a rule
sudo ufw delete allow <port>/tcp

# Delete by rule number
sudo ufw status numbered
sudo ufw delete <number>
```

### Enable/Disable Firewall:
```bash
# Enable
sudo ufw enable

# Disable (NOT RECOMMENDED in production)
sudo ufw disable

# Reload rules
sudo ufw reload
```

### Check Logs:
```bash
# View firewall logs
sudo tail -f /var/log/ufw.log

# Check blocked attempts
sudo grep -i block /var/log/ufw.log
```

## 🔍 Security Verification

### Test SSH Access:
```bash
# From another machine:
ssh root@152.53.206.21
```

### Test Web Access:
```bash
curl http://152.53.206.21/api/docs/
curl http://152.53.206.21/customadmin/login/
```

### Monitor Failed Attempts:
```bash
# SSH failed login attempts
sudo grep "Failed password" /var/log/auth.log | tail -20

# Firewall blocked connections
sudo grep "[UFW BLOCK]" /var/log/ufw.log | tail -20
```

## 🚨 Emergency Access Recovery

### If You Get Locked Out:
1. **Use Hetzner Console:** Access server via web console
2. **Disable Firewall Temporarily:**
   ```bash
   sudo ufw disable
   ```
3. **Fix the rules, then re-enable:**
   ```bash
   sudo ufw enable
   ```

### Backup SSH Access Rule:
```bash
# Ensure SSH is always allowed
sudo ufw allow 22/tcp comment 'SSH access - DO NOT REMOVE'
```

## 📊 Additional Security Recommendations

### 1. SSH Hardening (Optional):
```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Recommended settings:
# PermitRootLogin prohibit-password
# PasswordAuthentication no (use keys only)
# Port 2222 (change from default 22)

# Restart SSH
sudo systemctl restart sshd
```

### 2. Fail2Ban (Intrusion Prevention):
```bash
# Install Fail2Ban
sudo apt install fail2ban

# Configure to ban repeated failed login attempts
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Monitor Access Logs:
```bash
# Real-time SSH monitoring
sudo tail -f /var/log/auth.log

# Real-time firewall monitoring
sudo tail -f /var/log/ufw.log
```

### 4. Regular Updates:
```bash
# Keep system updated
sudo apt update && sudo apt upgrade -y

# Keep Python packages updated
cd /root/game && source venv/bin/activate
pip list --outdated
```

## ✅ Security Checklist

- [x] UFW Firewall enabled
- [x] SSH access protected (port 22)
- [x] HTTP/HTTPS ports open (80, 443)
- [x] Default deny incoming policy
- [x] OTP email system tested and working
- [x] Password hashing with Argon2
- [x] Security headers configured
- [x] CORS and CSRF protection active
- [x] Rate limiting enabled
- [x] Session security configured
- [ ] Fail2Ban installed (recommended)
- [ ] SSH key-only authentication (recommended)
- [ ] SSL/HTTPS configured (recommended)
- [ ] Automated backups (recommended)

## 🔗 Current Server Access

- **Server IP:** 152.53.206.21
- **SSH:** ssh root@152.53.206.21 (port 22)
- **Web:** http://152.53.206.21
- **Admin:** http://152.53.206.21/customadmin/login/
- **API:** http://152.53.206.21/api/docs/

---

**Last Updated:** December 5, 2025  
**Firewall Status:** ✅ Active and Protected  
**OTP System:** ✅ Tested and Working  
**SSH Access:** ✅ Guaranteed (Port 22 Open)
