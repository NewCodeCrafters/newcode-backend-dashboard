from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('internal/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name="schema"),
    path('api/schema/swagger-ui', SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path('api/schema/redoc', SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path('api/auth/', include('apps.users.urls')),
    path('students/', include('apps.students.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
