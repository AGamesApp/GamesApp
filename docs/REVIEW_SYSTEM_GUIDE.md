# Game Review System - Complete Guide

## Overview
The AGames review system has been redesigned to be **simple and user-friendly**. Each user can submit **one review per game**, combining both written feedback and optional rating in a single API call.

## Key Features

### ✅ One Review Per User Per Game
- Users can only have **one review** for each game
- Submitting a new review will **update** the existing one (no duplicates)
- Database enforces this with `unique_together` constraint on `(user, game)`

### ✅ Combined Review and Rating
- **Review text** (required): User's written feedback
- **Score** (optional): Rating from 1.0 to 5.0 in 0.5 increments
- Both can be submitted together in a **single API call**

### ✅ Complete User Information
All review responses include:
- `review`: The review text
- `score`: Rating (1.0-5.0) or null if not provided
- `profile_picture`: User's profile picture URL or null
- `username`: User's display name
- `comment_date`: Last update timestamp (ISO 8601)

## API Endpoints

### 1. Submit or Update Review
**Endpoint:** `POST /api/games/{game_id}/review/` or `PUT /api/games/{game_id}/review/`

**Authentication:** Required (Token)

**Request Body:**
```json
{
  "review": "This is an amazing game!",
  "score": 4.5
}
```

**Response (Created - 201):**
```json
{
  "message": "Review created successfully",
  "data": {
    "review": "This is an amazing game!",
    "score": 4.5,
    "profile_picture": "https://games.agames.cv/media/profile_pictures/user.jpg",
    "username": "johndoe",
    "comment_date": "2025-12-07T22:30:00Z"
  }
}
```

**Response (Updated - 200):**
```json
{
  "message": "Review updated successfully",
  "data": {
    "review": "Updated my review!",
    "score": 5.0,
    "profile_picture": "https://games.agames.cv/media/profile_pictures/user.jpg",
    "username": "johndoe",
    "comment_date": "2025-12-07T23:15:00Z"
  }
}
```

**Optional: Review Without Score**
```json
{
  "review": "Great game but haven't finished it yet."
}
```

### 2. Get All Reviews for a Game
**Endpoint:** `GET /api/games/{game_id}/reviews/`

**Authentication:** Not required

**Response (200):**
```json
{
  "count": 45,
  "next": "https://games.agames.cv/api/games/1/reviews/?page=2",
  "previous": null,
  "results": [
    {
      "id": 10,
      "review": "Amazing game!",
      "score": 4.5,
      "profile_picture": "https://games.agames.cv/media/profile_pictures/user1.jpg",
      "username": "johndoe",
      "comment_date": "2025-12-07T10:30:00Z"
    },
    {
      "id": 9,
      "review": "Good game but difficult controls",
      "score": 3.5,
      "profile_picture": null,
      "username": "janedoe",
      "comment_date": "2025-12-06T14:20:00Z"
    }
  ]
}
```

### 3. Get My Review for a Specific Game
**Endpoint:** `GET /api/games/{game_id}/my_review/`

**Authentication:** Required (Token)

**Response (200):**
```json
{
  "id": 10,
  "review": "Amazing game!",
  "score": 4.5,
  "profile_picture": "https://games.agames.cv/media/profile_pictures/user.jpg",
  "username": "johndoe",
  "comment_date": "2025-12-07T10:30:00Z"
}
```

**Response (404):**
```json
{
  "error": "You have not reviewed this game yet"
}
```

### 4. Get All My Reviews
**Endpoint:** `GET /api/games/my_reviews/`

**Authentication:** Required (Token)

**Response (200):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 10,
      "game_id": 1,
      "game_title": "Super Mario 64",
      "review": "Amazing game!",
      "score": 4.5,
      "profile_picture": "https://games.agames.cv/media/profile_pictures/user.jpg",
      "username": "johndoe",
      "comment_date": "2025-12-07T10:30:00Z"
    }
  ]
}
```

## Validation Rules

### Review Text
- **Required** for all submissions
- Cannot be empty or whitespace-only
- Automatically trimmed of leading/trailing whitespace

### Score
- **Optional** - can be omitted entirely
- If provided, must be between **1.0 and 5.0**
- Must be in **0.5 increments**: 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0
- Invalid values return clear error messages

### Examples of Valid Scores
✅ 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0

### Examples of Invalid Scores
❌ 0.5 (too low)  
❌ 6.0 (too high)  
❌ 4.3 (not in 0.5 increment)  
❌ 2.7 (not in 0.5 increment)

## Error Responses

### Missing Review Text (400)
```json
{
  "error": "Review text is required"
}
```

### Invalid Score Range (400)
```json
{
  "error": "Score must be between 1 and 5"
}
```

### Invalid Score Increment (400)
```json
{
  "error": "Score must be in 0.5 increments (e.g., 1.0, 1.5, 2.0)"
}
```

### Unauthorized (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Database Schema

### GameReview Model
```python
class GameReview(models.Model):
    user = ForeignKey(User)
    game = ForeignKey(Game)
    review = TextField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'game']  # Enforces one review per user per game
```

### GameRating Model
```python
class GameRating(models.Model):
    user = ForeignKey(User)
    game = ForeignKey(Game)
    score = DecimalField(max_digits=2, decimal_places=1)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'game']  # Enforces one rating per user per game
```

## Implementation Details

### Update or Create Logic
```python
# Reviews use update_or_create
review_obj, created = GameReview.objects.update_or_create(
    user=user,
    game=game,
    defaults={'review': review_text.strip()}
)

# Ratings also use update_or_create
if score is not None:
    GameRating.objects.update_or_create(
        user=user,
        game=game,
        defaults={'score': score}
    )
```

### Response Data
```python
response_data = {
    'review': review_obj.review,
    'score': rating.score if rating exists else None,
    'profile_picture': user.profile_picture.url if exists else None,
    'username': user.username,
    'comment_date': review_obj.updated_at
}
```

## Testing

Run the comprehensive test suite:
```bash
cd /root/game
./test_review_system.sh
```

Tests include:
1. ✅ Creating new review with score
2. ✅ Updating existing review (no duplicates)
3. ✅ Creating review without score
4. ✅ Adding score to existing review
5. ✅ Getting user's own review
6. ✅ Getting all reviews for a game
7. ✅ Getting all user's reviews
8. ✅ Error handling: missing review
9. ✅ Error handling: invalid score
10. ✅ Error handling: invalid increment

## Migration Applied

Migration file: `games/migrations/0023_alter_gamereview_unique_together.py`

This migration adds the `unique_together` constraint to prevent duplicate reviews. Before applying, the migration system automatically cleaned up any existing duplicates by keeping only the most recent review for each user-game pair.

## Benefits

### For Users
- **Simple**: One endpoint for both review and rating
- **Flexible**: Can submit review alone, or review + rating together
- **No Duplicates**: Update your review anytime without creating duplicates
- **Complete Info**: See reviewer's name, picture, and when they commented

### For Developers
- **Clean API**: Single endpoint handles create and update
- **Database Integrity**: Enforced at DB level with unique constraint
- **Efficient Queries**: Optimized with select_related for user data
- **Clear Errors**: Validation provides helpful error messages

### For the Platform
- **Data Quality**: No duplicate reviews cluttering the database
- **User Experience**: Users can easily update their opinions
- **Performance**: Fewer database records, faster queries
- **Trust**: One review per user prevents spam/manipulation
