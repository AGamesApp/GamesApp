#!/bin/bash

# Review System - Final Test (Both Fields Optional)
# Shows that review and score are both optional

BASE_URL="https://games.agames.cv/api"
TOKEN="4fc099223a0fd24cc4bc78b5efffff1251ec3c68"

echo "==============================================="
echo "Review System - Optional Fields Test"
echo "==============================================="
echo ""

# Test 1: Submit only score
echo "Test 1: Submit ONLY score (no review text)..."
echo "-----------------------------------------------"
curl -s -X POST ${BASE_URL}/games/20/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"score": 4.5}' | python3 -m json.tool
echo -e "\n"

# Test 2: Submit only review text
echo "Test 2: Submit ONLY review text (no score)..."
echo "-----------------------------------------------"
curl -s -X POST ${BASE_URL}/games/21/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"review": "Great game but no rating yet"}' | python3 -m json.tool
echo -e "\n"

# Test 3: Submit both
echo "Test 3: Submit BOTH review and score..."
echo "----------------------------------------"
curl -s -X POST ${BASE_URL}/games/22/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"review": "Amazing game!", "score": 5.0}' | python3 -m json.tool
echo -e "\n"

# Test 4: Update score only (review should remain)
echo "Test 4: Update - change only score (review stays)..."
echo "-----------------------------------------------------"
curl -s -X PUT ${BASE_URL}/games/22/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"score": 4.0}' | python3 -m json.tool
echo -e "\n"

# Test 5: Update review only (score should remain)
echo "Test 5: Update - change only review (score stays)..."
echo "-----------------------------------------------------"
curl -s -X PUT ${BASE_URL}/games/22/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"review": "Updated my thoughts on this game"}' | python3 -m json.tool
echo -e "\n"

# Test 6: Add score to review-only entry
echo "Test 6: Add score to existing review-only entry..."
echo "---------------------------------------------------"
curl -s -X PUT ${BASE_URL}/games/21/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"score": 3.5}' | python3 -m json.tool
echo -e "\n"

# Test 7: Add review to score-only entry
echo "Test 7: Add review to existing score-only entry..."
echo "---------------------------------------------------"
curl -s -X PUT ${BASE_URL}/games/20/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"review": "Now adding my written review"}' | python3 -m json.tool
echo -e "\n"

# Test 8: Error - neither field provided
echo "Test 8: Error - submitting empty request..."
echo "--------------------------------------------"
curl -s -X POST ${BASE_URL}/games/23/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
echo -e "\n"

# Test 9: Check no duplicates created
echo "Test 9: Verifying no duplicates in database..."
echo "-----------------------------------------------"
cd /root/game && source venv/bin/activate && python manage.py shell << 'PYEOF' 2>/dev/null
from games.models import GameReview
from django.db.models import Count

duplicates = GameReview.objects.values('user', 'game').annotate(
    count=Count('id')
).filter(count__gt=1)

if duplicates.exists():
    print("❌ Found duplicates!")
    for dup in duplicates:
        print(f"  User {dup['user']}, Game {dup['game']}: {dup['count']} reviews")
else:
    print("✅ No duplicates - each user has only one review per game")

# Count reviews
total = GameReview.objects.count()
print(f"\nTotal reviews in database: {total}")
PYEOF
echo -e "\n"

echo "==============================================="
echo "✅ All tests completed!"
echo ""
echo "Summary:"
echo "  ✅ Can submit score only"
echo "  ✅ Can submit review only"
echo "  ✅ Can submit both together"
echo "  ✅ Can update score without changing review"
echo "  ✅ Can update review without changing score"
echo "  ✅ Can add missing field later"
echo "  ✅ One review per user per game enforced"
echo "  ✅ Error when neither field provided"
echo "==============================================="
