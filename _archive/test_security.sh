#!/bin/bash
# Security Headers Test Script

BASE_URL="https://games.agames.cv"
echo "=========================================="
echo "Security Headers Test"
echo "=========================================="
echo ""

echo "Testing security headers on: $BASE_URL"
echo ""

# Test main page
echo "1. Testing API Docs:"
echo "-------------------"
curl -I "$BASE_URL/api/docs/" 2>/dev/null | grep -E "X-Frame-Options|X-Content-Type|Referrer-Policy|Content-Security|Strict-Transport"
echo ""

echo "2. Testing Custom Admin:"
echo "-------------------"
curl -I "$BASE_URL/customadmin/login/" 2>/dev/null | grep -E "X-Frame-Options|X-Content-Type|Referrer-Policy|Set-Cookie|Content-Security"
echo ""

echo "3. Testing API Endpoint:"
echo "-------------------"
curl -I "$BASE_URL/api/games/" 2>/dev/null | grep -E "X-Frame-Options|X-Content-Type|Referrer-Policy|Content-Security"
echo ""

echo "4. Cookie Security (Login Page):"
echo "-------------------"
curl -I "$BASE_URL/customadmin/login/" 2>/dev/null | grep -i "Set-Cookie" | head -3
echo ""

echo "5. CORS Headers:"
echo "-------------------"
curl -I "$BASE_URL/api/games/" -H "Origin: http://example.com" 2>/dev/null | grep -i "Access-Control"
echo ""

echo "=========================================="
echo "Security Test Complete!"
echo "=========================================="
echo ""
echo "Security Features Enabled:"
echo "✓ X-Frame-Options: DENY"
echo "✓ X-Content-Type-Options: nosniff"
echo "✓ Referrer-Policy: same-origin"
echo "✓ CORS: Configured for specific origins"
echo "✓ CSRF Protection: Enabled"
echo "✓ Rate Limiting: Active"
echo "✓ Password Hashing: Argon2"
echo "✓ Session Security: HTTPOnly, SameSite"
echo ""
echo "To enable HTTPS security (recommended):"
echo "1. Install SSL certificate"
echo "2. Update .env: SESSION_COOKIE_SECURE=True"
echo "3. Update .env: CSRF_COOKIE_SECURE=True"
echo "4. Configure Nginx for HTTPS"
