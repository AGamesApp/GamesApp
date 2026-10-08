# Fix Email Going to Spam - DKIM Configuration

## Problem
Password reset OTP emails are going to spam folder.

## Root Causes Fixed
1. ✅ **Reverse DNS (PTR)** - Already fixed (152.53.206.21 → games.agames.cv)
2. ✅ **SPF Record** - Already configured (v=spf1 a mx ip4:152.53.206.21 ~all)
3. ✅ **DMARC Record** - Already configured (v=DMARC1; p=none; rua=mailto:admin@games.agames.cv)
4. ⏳ **DKIM Signing** - Just installed and configured (needs DNS record)

## What Was Done
- Installed OpenDKIM for email signing
- Generated DKIM keys for games.agames.cv domain
- Configured Postfix to sign all outgoing emails with DKIM
- OpenDKIM service is running and active

## Required Action: Add DKIM DNS Record

### In Netcup DNS Manager:

**Record Type:** TXT  
**Name:** `mail._domainkey`  
**TTL:** 3600  
**Value:**
```
v=DKIM1; h=sha256; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2Hov01QwSy5cF2IdQ2PGIJY5EdLI7u+CUuDy9V68eudEbkT++1LiJogRQhQIENua2jRK8qIDldnrgKfplazKiQi2ZUFxEaux/sWEyuwwUUUoO6epnjGQxlfklGZ7Rkjx3hstefncvTammSlIT7Su7YA24d1w0yAAzAAmWDn7MF2NzSQCyX5144y2pqIoUT0Qq3ip6zQz3XKY9xbMKf1wloeYkrg7xcHUxJolWy1zwZVJ0Kv8ukTCWXMW+VtI26q3PIQQN+1neNV3sjqNqvSph7PoO6rjNCbovBuYIFVctI2xH3ovf6ORRdhhaADcKSEeXeBxTJxeyVIdUq+hYKOCjwIDAQAB
```

### Steps in Netcup:
1. Log into Netcup Customer Control Panel
2. Go to DNS zone for games.agames.cv
3. Click "Add Record"
4. Select Type: **TXT**
5. Enter Name: **mail._domainkey**
6. Paste the value above (entire long string)
7. Set TTL: **3600**
8. Save

## Verification

After adding the DNS record (wait 15-30 minutes for propagation), test with:

```bash
dig TXT mail._domainkey.games.agames.cv +short
```

You should see the DKIM record.

## Current DNS Records Summary

After adding DKIM, you will have all 4 essential email authentication records:

1. **SPF:** `v=spf1 a mx ip4:152.53.206.21 ~all`
2. **DMARC:** `v=DMARC1; p=none; rua=mailto:admin@games.agames.cv`
3. **PTR (Reverse DNS):** `152.53.206.21` → `games.agames.cv`
4. **DKIM:** `mail._domainkey.games.agames.cv` → (public key above)

## Expected Result

Once DKIM DNS record is added:
- ✅ All emails will be signed with DKIM
- ✅ Emails will pass SPF, DKIM, and DMARC checks
- ✅ Password reset OTPs will go to **INBOX** instead of spam
- ✅ Email deliverability score will improve significantly

## Testing After Setup

Send a test password reset email:
```bash
curl -X POST https://games.agames.cv/api/users/password-reset/request/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

Check email headers - you should see:
- `DKIM-Signature: v=1; a=rsa-sha256; d=games.agames.cv`
- `Authentication-Results: ... dkim=pass`

---

**Status:** DKIM installed and configured on server ✅  
**Next Step:** Add DNS record in Netcup ⏳  
**ETA:** Emails should reach inbox within 30 minutes of DNS propagation
