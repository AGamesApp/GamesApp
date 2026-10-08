#!/bin/bash
# Quick verification that review system is working

echo "🔍 Verifying Review System..."
echo "=============================="
echo ""

# 1. Test creating a review
echo "1️⃣ Creating new review for game 5..."
RESULT=$(curl -s -X POST https://games.agames.cv/api/games/5/review/ \
  -H "Authorization: Token 4fc099223a0fd24cc4bc78b5efffff1251ec3c68" \
  -H "Content-Type: application/json" \
  -d '{"review": "Spider-Man 3 is great!", "score": 4.0}')

if echo "$RESULT" | grep -q "created successfully"; then
    echo "   ✅ Created successfully"
else
    echo "   ❌ Failed to create"
fi
echo ""

# 2. Test updating the same review
echo "2️⃣ Updating same review (should not duplicate)..."
RESULT=$(curl -s -X PUT https://games.agames.cv/api/games/5/review/ \
  -H "Authorization: Token 4fc099223a0fd24cc4bc78b5efffff1251ec3c68" \
  -H "Content-Type: application/json" \
  -d '{"review": "Spider-Man 3 updated review!", "score": 4.5}')

if echo "$RESULT" | grep -q "updated successfully"; then
    echo "   ✅ Updated successfully (no duplicate)"
else
    echo "   ❌ Failed to update"
fi
echo ""

# 3. Check database for duplicates
echo "3️⃣ Checking database for duplicates..."
cd /root/game && source venv/bin/activate && python manage.py shell << 'PYEOF' 2>/dev/null
from games.models import GameReview
from django.db.models import Count

duplicates = GameReview.objects.values('user', 'game').annotate(
    count=Count('id')
).filter(count__gt=1)

if duplicates.exists():
    print("   ❌ Found duplicates in database!")
else:
    print("   ✅ No duplicates - database is clean!")
PYEOF
echo ""

# 4. Test getting own review
echo "4️⃣ Getting user's review for game 5..."
RESULT=$(curl -s -X GET https://games.agames.cv/api/games/5/my_review/ \
  -H "Authorization: Token 4fc099223a0fd24cc4bc78b5efffff1251ec3c68")

if echo "$RESULT" | grep -q "username"; then
    echo "   ✅ Retrieved with complete user info"
else
    echo "   ❌ Failed to retrieve"
fi
echo ""

# 5. Verify response has all required fields
echo "5️⃣ Verifying response has all required fields..."
if echo "$RESULT" | grep -q "review" && \
   echo "$RESULT" | grep -q "score" && \
   echo "$RESULT" | grep -q "username" && \
   echo "$RESULT" | grep -q "comment_date"; then
    echo "   ✅ All fields present: review, score, username, comment_date"
else
    echo "   ❌ Missing required fields"
fi
echo ""

echo "=============================="
echo "✅ Review System Verification Complete!"
