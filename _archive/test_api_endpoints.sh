#!/bin/bash
# AGames API Test Script
# Tests all API endpoints to verify deployment

BASE_URL="https://games.agames.cv"
echo "=========================================="
echo "AGames API Endpoint Testing"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    
    if [ "$method" == "GET" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$url")
    else
        status=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BASE_URL$url" -H "Content-Type: application/json" -d '{}')
    fi
    
    if [ $status -eq 200 ] || [ $status -eq 201 ] || [ $status -eq 400 ] || [ $status -eq 401 ] || [ $status -eq 405 ]; then
        echo -e "${GREEN}✓${NC} $name: $status"
    else
        echo -e "${RED}✗${NC} $name: $status"
    fi
}

echo "1. Documentation & Schema"
echo "-------------------------"
test_endpoint "API Documentation" "/api/docs/"
test_endpoint "API Schema" "/api/schema/"
echo ""

echo "2. Games API"
echo "-------------------------"
test_endpoint "Games List" "/api/games/"
test_endpoint "Emulators List" "/api/emulators/"
echo ""

echo "3. Users API"
echo "-------------------------"
test_endpoint "Register (POST)" "/api/users/register/" "POST"
test_endpoint "Login (POST)" "/api/users/login/" "POST"
test_endpoint "Profile (requires auth)" "/api/users/profile/"
test_endpoint "Verify OTP (POST)" "/api/users/verify-otp/" "POST"
test_endpoint "Resend OTP (POST)" "/api/users/resend-otp/" "POST"
test_endpoint "Google Login (POST)" "/api/users/google-login/" "POST"
echo ""

echo "4. Subscriptions API"
echo "-------------------------"
test_endpoint "Plans List" "/api/plans/"
test_endpoint "My Subscription" "/api/subscriptions/my-subscription/"
echo ""

echo "5. Payments API"
echo "-------------------------"
test_endpoint "Create Payment (POST)" "/api/payments/create/" "POST"
test_endpoint "Payment History" "/api/payments/history/"
echo ""

echo "6. Pages API"
echo "-------------------------"
test_endpoint "Page Detail (about)" "/api/pages/about/"
test_endpoint "Page Detail (privacy)" "/api/pages/privacy/"
echo ""

echo "7. Notifications API"
echo "-------------------------"
test_endpoint "Device Tokens" "/api/notifications/devices/"
test_endpoint "Notification Logs" "/api/notifications/logs/"
echo ""

echo "8. Support API"
echo "-------------------------"
test_endpoint "Submit Message (POST)" "/api/support/api/messages/" "POST"
test_endpoint "Support Messages" "/api/support/api/messages/"
echo ""

echo "9. Custom Admin"
echo "-------------------------"
test_endpoint "Admin Login" "/customadmin/login/"
test_endpoint "Admin Dashboard" "/customadmin/"
echo ""

echo "=========================================="
echo "Testing Complete!"
echo "=========================================="
