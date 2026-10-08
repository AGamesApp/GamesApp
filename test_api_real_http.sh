#!/bin/bash
#
# Test all API endpoints with real HTTP requests
#

echo "================================================================================"
echo "🧪 TESTING API ENDPOINTS WITH REAL HTTP REQUESTS"
echo "================================================================================"

# Base URL
BASE_URL="https://games.agames.cv"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# ============================================================================
# Helper function to test endpoint
# ============================================================================
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    local token=$5
    
    echo ""
    echo "--------------------------------------------------------------------------------"
    echo "TEST: $description"
    echo "      $method $endpoint"
    echo "--------------------------------------------------------------------------------"
    
    if [ -n "$token" ]; then
        HEADERS="-H 'Authorization: Token $token' -H 'Content-Type: application/json'"
    else
        HEADERS="-H 'Content-Type: application/json'"
    fi
    
    if [ -n "$data" ]; then
        if [ -n "$token" ]; then
            RESPONSE=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
                -H "Authorization: Token $token" \
                -H "Content-Type: application/json" \
                -d "$data")
        else
            RESPONSE=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
                -H "Content-Type: application/json" \
                -d "$data")
        fi
    else
        if [ -n "$token" ]; then
            RESPONSE=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
                -H "Authorization: Token $token" \
                -H "Content-Type: application/json")
        else
            RESPONSE=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
                -H "Content-Type: application/json")
        fi
    fi
    
    # Extract HTTP code (last line)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    # Extract body (all except last line)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    echo "Status Code: $HTTP_CODE"
    
    # Check if successful
    if [[ "$HTTP_CODE" =~ ^2[0-9]{2}$ ]]; then
        echo -e "${GREEN}✅ PASS${NC}"
        echo "Response: $BODY" | jq '.' 2>/dev/null || echo "$BODY"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Response: $BODY"
        ((FAILED++))
    fi
}

# ============================================================================
# Setup: Create test user and get token
# ============================================================================
echo ""
echo "================================================================================"
echo "SETUP: Creating test user and getting auth token"
echo "================================================================================"

# Register test user
TEST_EMAIL="apitest$(date +%s)@example.com"
REGISTER_DATA="{\"email\":\"$TEST_EMAIL\",\"username\":\"apitest\",\"password\":\"TestPass123!\",\"password_confirm\":\"TestPass123!\"}"

REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/users/register/" \
    -H "Content-Type: application/json" \
    -d "$REGISTER_DATA")

HTTP_CODE=$(echo "$REGISTER_RESPONSE" | tail -n1)
BODY=$(echo "$REGISTER_RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" =~ ^2[0-9]{2}$ ]]; then
    AUTH_TOKEN=$(echo "$BODY" | jq -r '.token' 2>/dev/null)
    echo -e "${GREEN}✅ User registered successfully${NC}"
    echo "Email: $TEST_EMAIL"
    echo "Token: ${AUTH_TOKEN:0:20}..."
else
    # Try to login if user exists
    LOGIN_DATA="{\"email\":\"test@endpoint.com\",\"password\":\"testpass123\"}"
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/users/login/" \
        -H "Content-Type: application/json" \
        -d "$LOGIN_DATA")
    AUTH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token' 2>/dev/null)
    if [ "$AUTH_TOKEN" != "null" ] && [ -n "$AUTH_TOKEN" ]; then
        echo -e "${GREEN}✅ Logged in with existing user${NC}"
    else
        echo -e "${RED}❌ Could not create or login user${NC}"
        echo "Response: $BODY"
        exit 1
    fi
fi

# ============================================================================
# TEST 1: Mark all notifications as read
# ============================================================================
test_endpoint "POST" "/api/notifications/mark_all_read/" \
    "Mark all notifications as read" \
    "" \
    "$AUTH_TOKEN"

# ============================================================================
# TEST 2: Get my loved games (favourites)
# ============================================================================
test_endpoint "GET" "/api/games/my_loved_games/" \
    "Get my favourite/loved games" \
    "" \
    "$AUTH_TOKEN"

# ============================================================================
# TEST 3: Send message to support
# ============================================================================
SUPPORT_DATA='{"name":"API Test User","email":"apitest@example.com","subject":"API Test Message","message":"This is a test message from the API test script"}'

test_endpoint "POST" "/api/support/messages/" \
    "Send message to support" \
    "$SUPPORT_DATA" \
    ""

# ============================================================================
# TEST 4: Get pages created from dashboard
# ============================================================================
test_endpoint "GET" "/api/pages/about-us/" \
    "Get page created from dashboard (about-us)" \
    "" \
    ""

# Try another page
test_endpoint "GET" "/api/pages/privacy/" \
    "Get page created from dashboard (privacy)" \
    "" \
    ""

# ============================================================================
# BONUS TESTS: Verify other endpoints mentioned in docs
# ============================================================================
test_endpoint "GET" "/api/notifications/unread/" \
    "Get unread notifications" \
    "" \
    "$AUTH_TOKEN"

test_endpoint "GET" "/api/games/games/" \
    "List games" \
    "" \
    ""

test_endpoint "GET" "/api/emulators/" \
    "List emulators" \
    "" \
    ""

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "================================================================================"
echo "📊 TEST SUMMARY"
echo "================================================================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total:  $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi
