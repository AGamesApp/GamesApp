# AGames Backend

Django REST API for AGames - a mobile app that lets users download games through different emulators.

## Features

- **User Authentication**: 
  - ✅ Email/Password registration and login
  - ✅ Email verification with OTP (One-Time Password)
  - ✅ Password reset with OTP
  - ✅ **Google Sign-In** - "Continue with Google" support
  - ✅ Token-based authentication
- **Subscription Plans**: Free and paid subscription tiers with different access levels
  - ✅ Automatic premium status when users subscribe
  - ✅ Django signals for subscription management
- **Game Management**: Browse, search, and filter games by emulator, genre, and rating
- **Game Ratings**: Users can rate and review games
- **Download Tracking**: Track game downloads for analytics
- **Payment Integration**: Stripe payment integration for premium subscriptions
- **Admin Panel**: Custom admin interface for managing users, games, and subscriptions
- **Email System**: Beautiful HTML emails with purple gradient theme

## Technology Stack

- **Framework**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL (configurable, defaults to SQLite for development)
- **Authentication**: Django Allauth with Google OAuth2
- **Payments**: Stripe API
- **Documentation**: drf-spectacular (Swagger/OpenAPI)

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL (optional, SQLite used by default)
- Stripe account (for payment features)
- Google OAuth2 credentials (for social login)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Ramyrashad127/game.git
cd game
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Update the `.env` file with your configuration:
   - Set `SECRET_KEY` to a secure random string
   - Configure database settings (optional)
   - Add Google OAuth2 credentials
   - Add Stripe API keys

6. Run migrations:
```bash
python manage.py migrate
```

7. Create a superuser:
```bash
python manage.py createsuperuser
```

8. Run the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/api/docs/
- **API Schema**: http://localhost:8000/api/schema/
- **Admin Panel**: http://localhost:8000/admin/

## API Endpoints

### Authentication
- `POST /api/users/register/` - User registration (with email OTP verification)
- `POST /api/users/verify-email/` - Verify email with OTP
- `POST /api/users/resend-otp/` - Resend OTP code
- `POST /api/users/login/` - User login
- `POST /api/users/logout/` - User logout
- `GET/PUT /api/users/profile/` - Get/update user profile
- `POST /api/users/request-password-reset/` - Request password reset OTP
- `POST /api/users/reset-password/` - Reset password with OTP
- `POST /api/users/auth/google/` - **Google Sign-In** (recommended)
- `POST /api/users/auth/google/login/` - Google OAuth login (advanced)

### Games
- `GET /api/games/` - List all games
- `GET /api/games/{id}/` - Get game details
- `POST /api/games/{id}/download/` - Record a download
- `GET /api/games/{id}/ratings/` - Get game ratings
- `GET /api/emulators/` - List emulators

### Ratings
- `GET /api/ratings/` - List ratings
- `POST /api/ratings/` - Create a rating
- `GET /api/ratings/{id}/` - Get rating details
- `PUT /api/ratings/{id}/` - Update rating
- `DELETE /api/ratings/{id}/` - Delete rating

### Subscriptions
- `GET /api/plans/` - List subscription plans
- `GET /api/subscriptions/` - List user subscriptions
- `POST /api/subscriptions/subscribe/` - Create subscription
- `POST /api/subscriptions/{id}/cancel/` - Cancel subscription

### Payments
- `GET /api/payments/` - List user payments
- `POST /api/create-payment-intent/` - Create payment intent
- `POST /api/webhook/stripe/` - Stripe webhook endpoint

## Models

### User
Custom user model with email authentication, profile information, and premium status.

### Emulator
Game emulator platforms (e.g., PS2, GameBoy, etc.).

### Game
Game information including title, description, genre, emulator, ratings, and download tracking.

### GameRating
User ratings and reviews for games (1-5 stars).

### GameDownload
Track game downloads by users.

### SubscriptionPlan
Available subscription plans with pricing and features.

### Subscription
User subscriptions with status tracking and auto-renewal.

### Payment
Payment transaction records with Stripe integration.

## 📚 Documentation

- **API Documentation**: See `API_DOCS.md` for complete API reference
- **Google OAuth Setup**: See `GOOGLE_SETUP_CHECKLIST.md` for step-by-step Google Sign-In setup
- **Google Auth Guide**: See `GOOGLE_AUTH_GUIDE.md` for integration examples and troubleshooting
- **Quick Start**: See `QUICKSTART.md` for getting started guide

## Development

### Running Tests
```bash
python manage.py test
```

### Testing Google OAuth
```bash
python test_google_auth.py
```

### Creating Migrations
```bash
python manage.py makemigrations
```

### Applying Migrations
```bash
python manage.py migrate
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure ALLOWED_HOSTS
5. Set up CORS for your frontend domain
6. Use a production-ready web server (e.g., Gunicorn + Nginx)
7. Set up SSL/TLS certificates
8. Configure Stripe webhooks with production URL

## Security Notes

- Never commit `.env` file with sensitive credentials
- Use strong SECRET_KEY in production
- Keep dependencies updated
- Review and restrict CORS settings for production
- Implement rate limiting for API endpoints
- Regular security audits and updates

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the GitHub repository.
