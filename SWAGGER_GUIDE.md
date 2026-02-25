# Swagger API Documentation Guide

## ✅ Swagger/OpenAPI Documentation Added

The API now has full Swagger documentation using `drf-spectacular`.

## 📍 Access Points

### Swagger UI (Interactive Documentation)
**URL:** `http://localhost:8000/api/docs/`

This is the main interactive API documentation where you can:
- View all API endpoints
- See request/response schemas
- Test API endpoints directly
- See authentication requirements

### ReDoc (Alternative Documentation)
**URL:** `http://localhost:8000/api/redoc/`

Alternative documentation view with a clean, readable format.

### OpenAPI Schema (JSON/YAML)
**URL:** `http://localhost:8000/api/schema/`

Raw OpenAPI schema in JSON format. Can be imported into Postman, Insomnia, etc.

### API Root
**URL:** `http://localhost:8000/api/`

Redirects to Swagger UI documentation.

## 🔐 Authentication in Swagger

To test authenticated endpoints in Swagger:

1. First, use the `/api/auth/login/` endpoint to get a token
2. Click the "Authorize" button at the top of Swagger UI
3. Enter: `Token YOUR_TOKEN_HERE` (replace YOUR_TOKEN_HERE with the actual token)
4. Click "Authorize"
5. Now you can test protected endpoints

## 📝 Available Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user (requires auth)

### Profile
- `GET /api/profile/me/` - Get current user (requires auth)
- `GET /api/profile/profile/` - Get user profile (requires auth)
- `PUT /api/profile/profile/update/` - Update profile (requires auth)

## 🧪 Testing in Swagger

1. Open `http://localhost:8000/api/docs/`
2. Expand any endpoint
3. Click "Try it out"
4. Fill in the request body (if needed)
5. Click "Execute"
6. See the response below

## 📦 Features

- ✅ Full API documentation
- ✅ Request/Response schemas
- ✅ Authentication support
- ✅ Interactive testing
- ✅ Example requests
- ✅ Error responses documented

