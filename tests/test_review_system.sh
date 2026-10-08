#!/bin/bash

# AGames Review System Test Script
# Tests the new unified review and rating system

BASE_URL="https://games.agames.cv/api"
TOKEN="4fc099223a0fd24cc4bc78b5efffff1251ec3c68"

echo "==============================================="
echo "AGames Review System - Testing Suite"
echo "==============================================="
echo ""

# Test 1: Create a new review with score
echo "Test 1: Creating a new review with score..."
echo "-------------------------------------------"
curl -X POST ${BASE_URL}/games/3/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "review": "Grand Theft Auto Vice City Stories is an excellent PSP game with great story and gameplay!",
    "score": 4.5
  }' | python3 -m json.tool
echo -e "\n"

# Test 2: Update the review
echo "Test 2: Updating the same review (should not create duplicate)..."
echo "-------------------------------------------------------------------"
curl -X PUT ${BASE_URL}/games/3/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "review": "Updated: GTA Vice City Stories is amazing! The missions are so fun.",
    "score": 5.0
  }' | python3 -m json.tool
echo -e "\n"

# Test 3: Create review without score
echo "Test 3: Creating review without score (only review text)..."
echo "------------------------------------------------------------"
curl -X POST ${BASE_URL}/games/4/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "review": "FIFA 14 on PSP is pretty good for a handheld football game."
  }' | python3 -m json.tool
echo -e "\n"

# Test 4: Update to add score later
echo "Test 4: Updating the review to add a score..."
echo "----------------------------------------------"
curl -X PUT ${BASE_URL}/games/4/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "review": "FIFA 14 on PSP is pretty good for a handheld football game. Controls are smooth.",
    "score": 3.5
  }' | python3 -m json.tool
echo -e "\n"

# Test 5: Get user's own review for a game
echo "Test 5: Getting my review for game ID 3..."
echo "-------------------------------------------"
curl -X GET ${BASE_URL}/games/3/my_review/ \
  -H "Authorization: Token ${TOKEN}" | python3 -m json.tool
echo -e "\n"

# Test 6: Get all reviews for a game
echo "Test 6: Getting all reviews for game ID 1..."
echo "---------------------------------------------"
curl -X GET ${BASE_URL}/games/1/reviews/ | python3 -m json.tool
echo -e "\n"

# Test 7: Get all my reviews
echo "Test 7: Getting all my reviews across all games..."
echo "---------------------------------------------------"
curl -X GET ${BASE_URL}/games/my_reviews/ \
  -H "Authorization: Token ${TOKEN}" | python3 -m json.tool
echo -e "\n"

# Test 8: Error - Missing review text
echo "Test 8: Testing error handling - missing review text..."
echo "--------------------------------------------------------"
curl -X POST ${BASE_URL}/games/5/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "score": 4.0
  }' | python3 -m json.tool
echo -e "\n"

# Test 9: Error - Invalid score
echo "Test 9: Testing error handling - invalid score (6.0)..."
echo "--------------------------------------------------------"
curl -X POST ${BASE_URL}/games/6/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "review": "Test review",
    "score": 6.0
  }' | python3 -m json.tool
echo -e "\n"

# Test 10: Error - Invalid score increment
echo "Test 10: Testing error handling - invalid increment (4.3)..."
echo "-------------------------------------------------------------"
curl -X POST ${BASE_URL}/games/7/review/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "review": "Test review",
    "score": 4.3
  }' | python3 -m json.tool
echo -e "\n"

echo "==============================================="
echo "All tests completed!"
echo "==============================================="
