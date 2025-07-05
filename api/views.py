from django.shortcuts import render

# Create your views here.
# api/views.py
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from oscar.core.loading import get_model

Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Django Oscar Headless Backend is running',
        'timestamp': str(timezone.now()),
        'version': '1.0.0'
    })

@csrf_exempt
@require_http_methods(["GET"])
def api_status(request):
    """API status with basic statistics"""
    try:
        product_count = Product.objects.filter(is_public=True).count()
        category_count = Category.objects.filter(is_public=True).count()
        
        return JsonResponse({
            'status': 'operational',
            'version': '1.0.0',
            'environment': 'development' if settings.DEBUG else 'production',
            'statistics': {
                'products': product_count,
                'categories': category_count,
            },
            'endpoints': {
                'graphql': '/graphql/',
                'admin': '/admin/',
                'health': '/health/',
                'auth': {
                    'token': '/api/auth/token/',
                    'refresh': '/api/auth/token/refresh/',
                    'verify': '/api/auth/token/verify/',
                }
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_info(request):
    """API information and documentation"""
    return JsonResponse({
        'name': 'Django Oscar Headless API',
        'description': 'Headless e-commerce backend with GraphQL API',
        'version': '1.0.0',
        'documentation': {
            'graphql': '/graphql/',
            'admin': '/admin/',
        },
        'features': [
            'GraphQL API',
            'JWT Authentication',
            'Product Management',
            'Order Management',
            'Booking System',
            'Payment Integration (VNPAY)',
            'Category Management',
            'User Management',
        ],
        'technologies': [
            'Django',
            'Django Oscar',
            'GraphQL',
            'JWT',
            'SQLite/PostgreSQL',
        ]
    })