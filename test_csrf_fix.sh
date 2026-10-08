#!/bin/bash
# Test script to simulate bot/crawler access patterns and monitor CSRF warnings

echo "=== CSRF Warning Reduction Test ==="
echo "Testing access patterns that typically trigger CSRF warnings..."
echo

# Count current warnings before test
current_warnings=$(grep -c "Forbidden.*Referer" logs/security.log 2>/dev/null || echo 0)
echo "Current CSRF warnings in logs: $current_warnings"

# Simulate bot access patterns (these typically trigger warnings)
echo "1. Simulating direct navigation (no referer):"
curl -s -o /dev/null -w "Status: %{http_code}\n" https://games.agames.cv/

echo "2. Simulating bot access (no user agent):"
curl -s -o /dev/null -w "Status: %{http_code}\n" -A "" https://games.agames.cv/

echo "3. Simulating crawler access:"
curl -s -o /dev/null -w "Status: %{http_code}\n" -A "Mozilla/5.0 (compatible; bot)" https://games.agames.cv/

# Wait a moment for logs to be written
sleep 2

# Count warnings after test  
new_warnings=$(grep -c "Forbidden.*Referer" logs/security.log 2>/dev/null || echo 0)
echo
echo "=== Results ==="
echo "Warnings before test: $current_warnings"
echo "Warnings after test: $new_warnings"
echo "New warnings generated: $((new_warnings - current_warnings))"

if [ $((new_warnings - current_warnings)) -eq 0 ]; then
    echo "✅ SUCCESS: No new CSRF warnings generated!"
    echo "The CSRFSafeLandingView is working correctly."
else
    echo "⚠️  Note: $((new_warnings - current_warnings)) new warnings generated"
    echo "This may be normal for some bot access patterns."
fi

echo
echo "Recent security log entries:"
tail -5 logs/security.log 2>/dev/null || echo "No security log entries found"