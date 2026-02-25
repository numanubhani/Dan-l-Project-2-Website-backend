# VPulse Backend - Django REST API

Backend API for VPulse video betting and content platform.

## Setup Instructions

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
  - Body: `{ "username": "user", "email": "user@example.com", "password": "pass123", "password2": "pass123", "name": "User Name", "role": "VIEWER" }`
- `POST /api/auth/login/` - Login user
  - Body: `{ "username": "user", "password": "pass123" }`
  - Returns: `{ "user": {...}, "token": "..." }`
- `POST /api/auth/logout/` - Logout user (requires authentication)

### Profile
- `GET /api/profile/me/` - Get current user (requires authentication)
- `GET /api/profile/profile/` - Get user profile (requires authentication)
- `PUT /api/profile/profile/update/` - Update user profile (requires authentication)
  - Body: `{ "name": "New Name", "email": "new@example.com", "avatar_url": "https://..." }`

## Admin Panel

Access the Django admin panel at: `http://localhost:8000/admin/`

Login with the superuser credentials created during setup.

