# backend/urls.py - Minimal Headless Configuration
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Admin interface (optional for headless)
    path('admin/', admin.site.urls),
    
    # GraphQL endpoint (main API)
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=settings.DEBUG))),
    
    # JWT Authentication endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Health check endpoint
    path('health/', include('api.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# For production, you might want to add:
# - API versioning: path('api/v1/', include('api.v1.urls'))
# - Documentation: path('docs/', include('api.docs.urls'))
# - Monitoring: path('metrics/', include('api.metrics.urls'))

# api_urls.py
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from graphene_django.views import GraphQLView
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# urlpatterns = [
#     path('admin/', admin.site.urls),
    
#     # API endpoints
#     path('api/v1/', include('api.urls')),
#     path('api/v1/booking/', include('booking.urls')),
#     path('api/v1/payments/', include('payments.urls')),
    
#     # GraphQL
#     path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=settings.DEBUG))),
    
#     # JWT Auth
#     path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)