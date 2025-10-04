# Django REST Framework Custom Authentication

A comprehensive authentication system for Django REST Framework using JWT tokens with automatic API documentation.

## Features

- JWT-based authentication using `rest_framework_simplejwt`
- Ready-to-use authentication endpoints via `dj_rest_auth`
- Automatic interactive API documentation with `drf_spectacular`
- Swagger UI and ReDoc interfaces
- Token refresh and blacklist capabilities
- User registration, login, logout, and password management

## Tech Stack

- Django REST Framework
- drf-spectacular (API documentation)
- rest_framework_simplejwt (JWT authentication)
- dj-rest-auth (Authentication endpoints)

## Installation

### 1. Install Required Packages

```bash
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install dj-rest-auth
pip install drf-spectacular
```

### 2. Update Django Settings

Add the following to your `settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'dj_rest_auth',
    
    # Your apps
    # 'your_app',
]

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# dj-rest-auth Configuration
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'auth-token',
    'JWT_AUTH_REFRESH_COOKIE': 'refresh-token',
    'JWT_AUTH_HTTPONLY': False,
}

# Spectacular Settings (API Documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API Documentation',
    'DESCRIPTION': 'Custom authentication API with JWT tokens',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v1',
    
    # JWT Authentication Configuration
    'SECURITY': [
        {
            'Bearer': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    ],
    
    # Swagger UI Configuration
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
    
    # Additional Settings
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'Bearer': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
}
```

### 3. Configure URLs

Update your project's `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Authentication Endpoints
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # JWT Token Endpoints
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Your API endpoints
    # path('api/v1/', include('your_app.urls')),
]
```

### 4. Run Migrations

```bash
python manage.py migrate
```

## API Endpoints

### Authentication Endpoints

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/api/auth/login/` | POST | Login with username/email and password | No |
| `/api/auth/logout/` | POST | Logout (blacklist refresh token) | Yes |
| `/api/auth/user/` | GET | Get current user details | Yes |
| `/api/auth/password/reset/` | POST | Request password reset email | No |
| `/api/auth/password/reset/confirm/` | POST | Confirm password reset | No |
| `/api/auth/password/change/` | POST | Change password | Yes |
| `/api/token/refresh/` | POST | Refresh access token | No (requires refresh token) |
| `/api/token/verify/` | POST | Verify token validity | No |

### Registration Endpoints (Optional)

If you include `dj_rest_auth.registration`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/registration/` | POST | Register new user |
| `/api/auth/registration/verify-email/` | POST | Verify email address |

## Usage Examples

### 1. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "pk": 1,
    "username": "your_username",
    "email": "user@example.com"
  }
}
```

### 2. Access Protected Endpoint

```bash
curl -X GET http://localhost:8000/api/protected-endpoint/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 3. Refresh Token

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

### 4. Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Using Swagger UI

1. Navigate to http://localhost:8000/api/docs/
2. Click on `/api/auth/login/` endpoint
3. Click "Try it out"
4. Enter credentials and execute
5. Copy the `access` token from the response
6. Click the "Authorize" button at the top
7. Enter: `Bearer <your-access-token>`
8. Now you can test all protected endpoints

## Custom Authentication Views

Create custom views in your app:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get user profile",
        description="Retrieve the authenticated user's profile information",
        responses={200: {'type': 'object'}},
    )
    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })
```

## Security Considerations

1. **HTTPS**: Always use HTTPS in production
2. **Secret Key**: Keep your `SECRET_KEY` secure and never commit it to version control
3. **Token Lifetime**: Adjust token lifetimes based on your security requirements
4. **CORS**: Configure CORS properly if your frontend is on a different domain
5. **Token Storage**: Store tokens securely in the client (avoid localStorage for sensitive apps)

## Troubleshooting

### Issue: "Authentication credentials were not provided"
- Ensure you're including the Authorization header: `Authorization: Bearer <token>`
- Check that the token hasn't expired

### Issue: Token blacklist not working
- Add `rest_framework_simplejwt.token_blacklist` to INSTALLED_APPS
- Run migrations: `python manage.py migrate`

### Issue: Documentation not showing authentication
- Verify `DEFAULT_SCHEMA_CLASS` is set to `drf_spectacular.openapi.AutoSchema`
- Check that SPECTACULAR_SETTINGS includes the security configuration

## Additional Resources

- [DRF Spectacular Documentation](https://drf-spectacular.readthedocs.io/)
- [Simple JWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [dj-rest-auth Documentation](https://dj-rest-auth.readthedocs.io/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)

## License

This project configuration is open source and available under the MIT License.# newcode-backend-dashboard
