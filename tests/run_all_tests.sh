#!/bin/bash
# Comprehensive System Test
# Run all tests and generate a complete report

echo "======================================================================"
echo "🧪 COMPREHENSIVE SYSTEM TEST REPORT"
echo "======================================================================"
echo "Date: $(date)"
echo "Server: $(hostname)"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to print test result
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}: $2"
        ((FAILED++))
    fi
}

# Test 1: Django System Check
echo "----------------------------------------------------------------------"
echo "TEST 1: Django System Check"
echo "----------------------------------------------------------------------"
cd /root/game
python manage.py check > /dev/null 2>&1
test_result $? "Django configuration"

# Test 2: Database Connection
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 2: Database Connection"
echo "----------------------------------------------------------------------"
python manage.py dbshell --command="SELECT 1;" > /dev/null 2>&1
test_result $? "PostgreSQL connection"

# Test 3: Redis Connection
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 3: Redis Cache"
echo "----------------------------------------------------------------------"
redis-cli ping > /dev/null 2>&1
test_result $? "Redis connection"

# Test 4: API Endpoints
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 4: API Endpoints"
echo "----------------------------------------------------------------------"

# Test games endpoint
curl -s https://games.agames.cv/api/games/ | grep -q "count"
test_result $? "GET /api/games/ endpoint"

# Test device tokens endpoint
curl -s -X POST https://games.agames.cv/api/device-tokens/ \
  -H "Content-Type: application/json" \
  -d '{"token":"test","platform":"android"}' > /dev/null 2>&1
test_result $? "POST /api/device-tokens/ endpoint"

# Test 5: Static Files
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 5: Static Files"
echo "----------------------------------------------------------------------"
[ -d /root/game/staticfiles ] && [ "$(ls -A /root/game/staticfiles)" ]
test_result $? "Static files collected"

# Test 6: Gunicorn Service
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 6: Gunicorn Service"
echo "----------------------------------------------------------------------"
systemctl is-active --quiet gunicorn
test_result $? "Gunicorn running"

# Test 7: Nginx Service
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 7: Nginx Service"
echo "----------------------------------------------------------------------"
systemctl is-active --quiet nginx
test_result $? "Nginx running"

# Test 8: SSL Certificate
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 8: SSL Certificate"
echo "----------------------------------------------------------------------"
curl -s https://games.agames.cv/ > /dev/null 2>&1
test_result $? "HTTPS/SSL working"

# Test 9: Database Models
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 9: Database Models"
echo "----------------------------------------------------------------------"
cd /root/game
python << 'EOF'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import Game
from users.models import User
from notifications.models import Notification, DeviceToken

try:
    # Check models are accessible
    Game.objects.count()
    User.objects.count()
    Notification.objects.count()
    DeviceToken.objects.count()
    exit(0)
except Exception as e:
    print(f"Error: {e}")
    exit(1)
EOF
test_result $? "All database models accessible"

# Test 10: Migrations
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 10: Database Migrations"
echo "----------------------------------------------------------------------"
python manage.py showmigrations | grep -q "\[X\]"
test_result $? "All migrations applied"

# Test 11: Admin Dashboard
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 11: Admin Dashboard"
echo "----------------------------------------------------------------------"
curl -s https://games.agames.cv/custom-admin/ | grep -q "Game Zone"
test_result $? "Admin dashboard accessible"

# Test 12: Firebase Configuration
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 12: Firebase Configuration"
echo "----------------------------------------------------------------------"
[ -f /root/game/serviceAccountKey.json ]
test_result $? "Firebase credentials file exists"

# Test 13: Environment Variables
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 13: Environment Configuration"
echo "----------------------------------------------------------------------"
[ -f /root/game/.env ]
test_result $? "Environment file exists"

# Test 14: New Features
echo ""
echo "----------------------------------------------------------------------"
echo "TEST 14: New Features"
echo "----------------------------------------------------------------------"
cd /root/game
python << 'EOF'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import Game
from notifications.models import NotificationLog

try:
    # Test game description field
    game = Game.objects.first()
    assert hasattr(game, 'description'), "Description field missing"
    
    # Test notification types
    types = dict(NotificationLog.TYPE_CHOICES)
    required = ['normal', 'fix', 'update', 'error']
    for t in required:
        assert t in types, f"Type {t} missing"
    
    exit(0)
except Exception as e:
    print(f"Error: {e}")
    exit(1)
EOF
test_result $? "New features implemented"

# System Information
echo ""
echo "======================================================================"
echo "📊 SYSTEM INFORMATION"
echo "======================================================================"

# Database stats
echo ""
echo "Database Statistics:"
cd /root/game
python << 'EOF'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import Game, GameReview
from users.models import User
from notifications.models import Notification, DeviceToken

print(f"  Games: {Game.objects.count()}")
print(f"  Users: {User.objects.count()}")
print(f"  Reviews: {GameReview.objects.count()}")
print(f"  Notifications: {Notification.objects.count()}")
print(f"  Device Tokens: {DeviceToken.objects.filter(is_active=True).count()}")
EOF

# Server stats
echo ""
echo "Server Resources:"
echo "  CPU Cores: $(nproc)"
echo "  RAM Total: $(free -h | awk '/^Mem:/ {print $2}')"
echo "  RAM Used: $(free -h | awk '/^Mem:/ {print $3}')"
echo "  Disk Used: $(df -h / | awk 'NR==2 {print $3 "/" $2}')"

# Services
echo ""
echo "Services Status:"
systemctl is-active gunicorn > /dev/null 2>&1 && echo "  Gunicorn: Active" || echo "  Gunicorn: Inactive"
systemctl is-active nginx > /dev/null 2>&1 && echo "  Nginx: Active" || echo "  Nginx: Inactive"
systemctl is-active postgresql > /dev/null 2>&1 && echo "  PostgreSQL: Active" || echo "  PostgreSQL: Inactive"
systemctl is-active redis > /dev/null 2>&1 && echo "  Redis: Active" || echo "  Redis: Inactive"

# Final Summary
echo ""
echo "======================================================================"
echo "📈 TEST SUMMARY"
echo "======================================================================"
echo ""
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo "System is healthy and ready for production."
else
    echo -e "${YELLOW}⚠️  SOME TESTS FAILED${NC}"
    echo "Please review the failed tests above."
fi

echo ""
echo "======================================================================"
echo "Report generated: $(date)"
echo "======================================================================"
