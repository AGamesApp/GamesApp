#!/bin/bash

echo "================================"
echo "AGames SSL/HTTPS Verification"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Certificate Info
echo "1. Certificate Information:"
echo "   -------------------------"
sudo certbot certificates 2>/dev/null | grep -A 6 "Certificate Name: games.agames.cv" || echo "   ${RED}✗ Certificate not found${NC}"
echo ""

# Test 2: HTTPS Response
echo "2. HTTPS Health Check:"
echo "   -------------------"
HTTPS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://games.agames.cv/health/ 2>/dev/null)
if [ "$HTTPS_RESPONSE" == "200" ]; then
    echo -e "   ${GREEN}✓ HTTPS working (HTTP $HTTPS_RESPONSE)${NC}"
else
    echo -e "   ${RED}✗ HTTPS failed (HTTP $HTTPS_RESPONSE)${NC}"
fi
echo ""

# Test 3: HTTP Redirect
echo "3. HTTP → HTTPS Redirect:"
echo "   ----------------------"
HTTP_REDIRECT=$(curl -s -o /dev/null -w "%{http_code}" http://games.agames.cv/health/ 2>/dev/null)
if [ "$HTTP_REDIRECT" == "301" ] || [ "$HTTP_REDIRECT" == "302" ]; then
    echo -e "   ${GREEN}✓ HTTP redirects to HTTPS (HTTP $HTTP_REDIRECT)${NC}"
else
    echo -e "   ${RED}✗ HTTP redirect failed (HTTP $HTTP_REDIRECT)${NC}"
fi
echo ""

# Test 4: Security Headers
echo "4. Security Headers:"
echo "   -----------------"
HEADERS=$(curl -I -s https://games.agames.cv/health/ 2>/dev/null)

if echo "$HEADERS" | grep -qi "strict-transport-security"; then
    echo -e "   ${GREEN}✓ HSTS header present${NC}"
else
    echo -e "   ${RED}✗ HSTS header missing${NC}"
fi

if echo "$HEADERS" | grep -qi "x-frame-options"; then
    echo -e "   ${GREEN}✓ X-Frame-Options present${NC}"
else
    echo -e "   ${RED}✗ X-Frame-Options missing${NC}"
fi

if echo "$HEADERS" | grep -qi "x-content-type-options"; then
    echo -e "   ${GREEN}✓ X-Content-Type-Options present${NC}"
else
    echo -e "   ${RED}✗ X-Content-Type-Options missing${NC}"
fi
echo ""

# Test 5: HTTP/2
echo "5. HTTP/2 Support:"
echo "   ---------------"
if echo "$HEADERS" | grep -q "HTTP/2"; then
    echo -e "   ${GREEN}✓ HTTP/2 enabled${NC}"
else
    echo -e "   ${RED}✗ HTTP/2 not detected${NC}"
fi
echo ""

# Test 6: Auto-Renewal Timer
echo "6. Certificate Auto-Renewal:"
echo "   -------------------------"
TIMER_STATUS=$(sudo systemctl is-active certbot.timer 2>/dev/null)
if [ "$TIMER_STATUS" == "active" ]; then
    echo -e "   ${GREEN}✓ Certbot timer active${NC}"
    NEXT_RUN=$(systemctl list-timers certbot.timer 2>/dev/null | grep certbot | awk '{print $1, $2, $3}')
    echo "   Next run: $NEXT_RUN"
else
    echo -e "   ${RED}✗ Certbot timer not active${NC}"
fi
echo ""

# Test 7: Service Status
echo "7. Service Health:"
echo "   ---------------"
for service in nginx gunicorn postgresql redis; do
    STATUS=$(sudo systemctl is-active $service 2>/dev/null)
    if [ "$STATUS" == "active" ]; then
        echo -e "   ${GREEN}✓ $service: running${NC}"
    else
        echo -e "   ${RED}✗ $service: $STATUS${NC}"
    fi
done
echo ""

# Test 8: Certificate Expiry
echo "8. Certificate Validity:"
echo "   ---------------------"
EXPIRY=$(openssl s_client -connect games.agames.cv:443 -servername games.agames.cv < /dev/null 2>/dev/null | openssl x509 -noout -enddate | sed 's/notAfter=//')
if [ -n "$EXPIRY" ]; then
    echo -e "   ${GREEN}✓ Expires: $EXPIRY${NC}"
else
    echo -e "   ${RED}✗ Could not determine expiry${NC}"
fi
echo ""

# Summary
echo "================================"
echo "Verification Complete"
echo "================================"
echo ""
echo "URLs:"
echo "  • Main: https://games.agames.cv"
echo "  • Health: https://games.agames.cv/health/"
echo "  • Admin: https://games.agames.cv/customadmin/"
echo ""
echo "Documentation:"
echo "  • Full SSL Guide: /root/game/docs/SSL_CONFIGURATION_COMPLETE.md"
echo "  • Quick Reference: /root/game/docs/deployment/HTTPS_QUICK_REFERENCE.md"
echo "  • Current Status: /root/game/docs/CURRENT_STATUS.md"
echo ""
