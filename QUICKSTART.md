# VPulse Backend - Quick Start Guide

## Quick Setup (Windows)

1. **Navigate to backend directory:**
   ```bash
   cd "D:\Dan L\Project 2\Website\backend\Dan-l-Project-2-Website-backend"
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create default admin user:**
   ```bash
   python manage.py create_default_admin
   ```

6. **Start the server:**
   ```bash
   python manage.py runserver
   ```

## Default Admin Credentials

- **Username:** `admin`
- **Email:** `admin@vpulse.com`
- **Password:** `admin123`

**⚠️ Important:** Change the password after first login!

## Access Points

- **API Base URL:** `http://localhost:8000/api/`
- **Admin Panel:** `http://localhost:8000/admin/`

## Testing the API

### Register a new user:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "password2": "test123",
    "name": "Test User"
  }'
```

### Login:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123"
  }'
```

### Get profile (requires token):
```bash
curl -X GET http://localhost:8000/api/profile/me/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## API Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | Login user | No |
| POST | `/api/auth/logout/` | Logout user | Yes |
| GET | `/api/profile/me/` | Get current user | Yes |
| GET | `/api/profile/profile/` | Get user profile | Yes |
| PUT | `/api/profile/profile/update/` | Update profile | Yes |

