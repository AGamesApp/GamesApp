#!/bin/bash
#
# Final test of all API endpoints
#

echo "================================================================================"
echo "🧪 FINAL API ENDPOINT TESTS"
echo "================================================================================"

BASE_URL="https://games.agames.cv"
PASSED=0
FAILED=0

# Get auth token (using existing test user)
echo ""
echo "Getting auth token..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/users/login/" \
    -H "Content-Type: application/json" \
    -d '{"email":"test@endpoint.com","password":"testpass123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token' 2>/dev/null)

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "⚠️  Could not get token, registering new user..."
    REG_EMAIL="test$(date +%s)@test.com"
    REG_RESPONSE=$(curl -s -X POST "$BASE_URL/api/users/register/" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$REG_EMAIL\",\"username\":\"testuser\",\"password\":\"Test123!\",\"password_confirm\":\"Test123!\"}")
    TOKEN=$(echo "$REG_RESPONSE" | jq -r '.token' 2>/dev/null)
fi

echo "Token: ${TOKEN:0:30}..."

# ============================================================================
# TEST 1: Mark all notifications as read
# ============================================================================
echo ""
echo "================================================================================"
echo "TEST 1: POST /api/notifications/mark_all_read/"
echo "================================================================================"

RESPONSE=$(curl -s -X POST "$BASE_URL/api/notifications/mark_all_read/" \
    -H "Authorization: Token $TOKEN" \
    -H "Content-Type: application/json")

if echo "$RESPONSE" | jq -e '.message' > /dev/null 2>&1; then
    echo "✅ PASS - Mark all notifications as read"
    echo "$RESPONSE" | jq '.'
    ((PASSED++))
else
    echo "❌ FAIL - Mark all notifications as read"
    echo "$RESPONSE"
    ((FAILED++))
fi

# ============================================================================
# TEST 2: Get my loved games
# ============================================================================
echo ""
echo "================================================================================"
echo "TEST 2: GET /api/games/my_loved_games/"
echo "================================================================================"

RESPONSE=$(curl -s -X GET "$BASE_URL/api/games/my_loved_games/" \
    -H "Authorization: Token $TOKEN" \
    -H "Content-Type: application/json")

if echo "$RESPONSE" | jq -e '.results' > /dev/null 2>&1; then
    echo "✅ PASS - Get my loved games"
    COUNT=$(echo "$RESPONSE" | jq -r '.count')
    echo "Found $COUNT loved games"
    ((PASSED++))
else
    echo "❌ FAIL - Get my loved games"
    echo "$RESPONSE"
    ((FAILED++))
fi

# ============================================================================
# TEST 3: Send message to support
# ============================================================================
echo ""
echo "================================================================================"
echo "TEST 3: POST /api/support/messages/"
echo "================================================================================"

SUPPORT_DATA='{"name":"Test User","email":"test@example.com","subject":"Test Support Message","message":"Testing the support endpoint"}'

RESPONSE=$(curl -s -X POST "$BASE_URL/api/support/messages/" \
    -H "Content-Type: application/json" \
    -d "$SUPPORT_DATA")

if echo "$RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    echo "✅ PASS - Send message to support"
    echo "$RESPONSE" | jq '.'
    ((PASSED++))
else
    echo "❌ FAIL - Send message to support"
    echo "$RESPONSE"
    ((FAILED++))
fi

# ============================================================================
# TEST 4: Get pages (with proper URL encoding)
# ============================================================================
echo ""
echo "================================================================================"
echo "TEST 4: GET /api/pages/About%20us/"
echo "================================================================================"

RESPONSE=$(curl -s -X GET "$BASE_URL/api/pages/About%20us/" \
    -H "Content-Type: application/json")

if echo "$RESPONSE" | jq -e '.title' > /dev/null 2>&1; then
    echo "✅ PASS - Get page 'About us'"
    TITLE=$(echo "$RESPONSE" | jq -r '.title')
    echo "Page title: $TITLE"
    ((PASSED++))
else
    echo "❌ FAIL - Get page 'About us'"
    echo "$RESPONSE"
    ((FAILED++))
fi

# ============================================================================
# BONUS: Test unread notifications
# ============================================================================
echo ""
echo "================================================================================"
echo "BONUS: GET /api/notifications/unread/"
echo "================================================================================"

RESPONSE=$(curl -s -X GET "$BASE_URL/api/notifications/unread/" \
    -H "Authorization: Token $TOKEN" \
    -H "Content-Type: application/json")

if echo "$RESPONSE" | jq -e '.count' > /dev/null 2>&1; then
    echo "✅ PASS - Get unread notifications"
    COUNT=$(echo "$RESPONSE" | jq -r '.count')
    echo "Unread count: $COUNT"
    ((PASSED++))
else
    echo "❌ FAIL - Get unread notifications"
    echo "$RESPONSE"
    ((FAILED++))
fi

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "================================================================================"
echo "📊 FINAL SUMMARY"
echo "================================================================================"
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo "Total:  $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All endpoints working correctly!"
else
    echo "⚠️  Some endpoints need attention"
fi
