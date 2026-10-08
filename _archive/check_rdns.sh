#!/bin/bash

echo "=================================="
echo "Checking rDNS for 152.53.206.21"
echo "=================================="
echo ""

CURRENT_RDNS=$(dig -x 152.53.206.21 +short)

echo "Current rDNS: $CURRENT_RDNS"
echo ""

if [[ "$CURRENT_RDNS" == "games.agames.cv." ]]; then
    echo "✅ SUCCESS! rDNS is now set to games.agames.cv"
    echo ""
    echo "Your emails should now go to INBOX instead of SPAM!"
    echo ""
    echo "Next steps:"
    echo "1. Send a test email:"
    echo "   curl -X POST https://games.agames.cv/api/users/password-reset/request/ \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"email\": \"ramy41599@gmail.com\"}' -k"
    echo ""
    echo "2. Check your Gmail inbox (not spam folder!)"
    echo ""
    echo "3. View email headers in Gmail:"
    echo "   - Open email → Three dots → 'Show original'"
    echo "   - Look for: 'Received-SPF: pass'"
    echo "   - Look for: 'DMARC: PASS'"
else
    echo "⏳ WAITING... rDNS still shows: $CURRENT_RDNS"
    echo ""
    echo "Expected: games.agames.cv."
    echo ""
    echo "DNS propagation can take 5-30 minutes."
    echo "Run this script again in a few minutes:"
    echo "  bash /root/game/check_rdns.sh"
fi

echo ""
echo "=================================="
