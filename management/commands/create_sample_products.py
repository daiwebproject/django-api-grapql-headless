from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from oscar.core.loading import get_model
from booking.models import ServiceCategory, Service
from decimal import Decimal

User = get_user_model()
Product = get_model('catalogue', 'Product')
ProductClass = get_model('catalogue', 'ProductClass')
Category = get_model('catalogue', 'Category')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')

class Command(BaseCommand):
    help = 'Create sample products and services for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing sample data before creating new ones',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️  Resetting sample data...')
            Product.objects.filter(title__startswith='Sample').delete()
            Service.objects.filter(name__startswith='Sample').delete()
        
        self.stdout.write('📦 Creating sample products and services...')
        
        # Create product categories
        electronics, created = Category.objects.get_or_create(
            name='Electronics',
            defaults={'slug': 'electronics', 'is_public': True, 'description': 'Electronic devices and gadgets'}
        )
        if created:
            self.stdout.write(f'✅ Created category: {electronics.name}')
        
        books, created = Category.objects.get_or_create(
            name='Books',
            defaults={'slug': 'books', 'is_public': True, 'description': 'Books and publications'}
        )
        if created:
            self.stdout.write(f'✅ Created category: {books.name}')
        
        # Create product class
        product_class, created = ProductClass.objects.get_or_create(
            name='Physical Product',
            defaults={'slug': 'physical-product', 'requires_shipping': True, 'track_stock': True}
        )
        if created:
            self.stdout.write(f'✅ Created product class: {product_class.name}')
        
        # Create partner
        partner, created = Partner.objects.get_or_create(
            name='Default Partner',
            defaults={'code': 'default'}
        )
        if created:
            self.stdout.write(f'✅ Created partner: {partner.name}')
        
        # Create sample products
        products_data = [
            ('iPhone 15 Pro', 'iphone-15-pro', electronics, 29990000, 'Latest iPhone with A17 Pro chip', 25),
            ('MacBook Pro 14"', 'macbook-pro-14', electronics, 52990000, 'Powerful laptop for professionals', 10),
            ('AirPods Pro 2', 'airpods-pro-2', electronics, 6990000, 'Wireless earbuds with ANC', 50),
            ('iPad Air', 'ipad-air', electronics, 17990000, 'Versatile tablet for work and play', 30),
            ('Apple Watch Series 9', 'apple-watch-series-9', electronics, 9990000, 'Advanced smartwatch', 40),
            ('Python Programming Book', 'python-programming-book', books, 499000, 'Learn Python from scratch', 100),
            ('Django for Beginners', 'django-beginners-book', books, 599000, 'Web development with Django', 75),
            ('React Complete Guide', 'react-complete-guide', books, 799000, 'Master React development', 60),
            ('GraphQL Handbook', 'graphql-handbook', books, 699000, 'API development with GraphQL', 80),
            ('Full Stack Development', 'fullstack-development-book', books, 899000, 'Complete web development guide', 45),
        ]
        
        created_products = 0
        for title, slug, category, price, description, stock in products_data:
            product, created = Product.objects.get_or_create(
                title=title,
                defaults={
                    'slug': slug,
                    'description': description,
                    'product_class': product_class,
                    'structure': Product.STANDALONE,
                    'is_public': True
                }
            )
            
            if created:
                product.categories.add(category)
                
                StockRecord.objects.get_or_create(
                    product=product,
                    partner=partner,
                    defaults={
                        'price': Decimal(str(price)),
                        'num_in_stock': stock,
                        'low_stock_threshold': 5
                    }
                )
                created_products += 1
                self.stdout.write(f'✅ Created product: {title}')
        
        # Create service categories
        consultation, created = ServiceCategory.objects.get_or_create(
            name='Consultation',
            defaults={'slug': 'consultation', 'description': 'Professional consultation services'}
        )
        if created:
            self.stdout.write(f'✅ Created service category: {consultation.name}')
        
        treatment, created = ServiceCategory.objects.get_or_create(
            name='Treatment',
            defaults={'slug': 'treatment', 'description': 'Medical treatment services'}
        )
        if created:
            self.stdout.write(f'✅ Created service category: {treatment.name}')
        
        therapy, created = ServiceCategory.objects.get_or_create(
            name='Therapy',
            defaults={'slug': 'therapy', 'description': 'Therapeutic services'}
        )
        if created:
            self.stdout.write(f'✅ Created service category: {therapy.name}')
        
        # Create services
        services_data = [
            ('General Consultation', 'general-consultation', consultation, 30, 500000, 'Basic health consultation'),
            ('Specialist Consultation', 'specialist-consultation', consultation, 45, 800000, 'Expert medical consultation'),
            ('Health Checkup', 'health-checkup', consultation, 60, 1200000, 'Comprehensive health examination'),
            ('Basic Treatment', 'basic-treatment', treatment, 60, 1000000, 'Standard medical treatment'),
            ('Advanced Treatment', 'advanced-treatment', treatment, 90, 1800000, 'Specialized medical treatment'),
            ('Emergency Treatment', 'emergency-treatment', treatment, 120, 2500000, 'Urgent medical care'),
            ('Physical Therapy', 'physical-therapy', therapy, 45, 600000, 'Rehabilitation and physical therapy'),
            ('Counseling Session', 'counseling-session', therapy, 60, 800000, 'Mental health counseling'),
            ('Group Therapy', 'group-therapy', therapy, 90, 400000, 'Group therapeutic session'),
        ]
        
        created_services = 0
        for name, slug, category, duration, price, description in services_data:
            service, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slug,
                    'category': category,
                    'description': description,
                    'duration_minutes': duration,
                    'price': Decimal(str(price)),
                    'is_active': True
                }
            )
            
            if created:
                created_services += 1
                self.stdout.write(f'✅ Created service: {name}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('🎉 Sample data creation completed!'))
        self.stdout.write(f'📦 Products created: {created_products}')
        self.stdout.write(f'🏥 Services created: {created_services}')
        self.stdout.write('\n📋 You can now:')
        self.stdout.write('   • Test GraphQL queries with: python manage.py test_graphql')
        self.stdout.write('   • Visit GraphiQL: http://localhost:8000/graphql/')
        self.stdout.write('   • Check admin panel: http://localhost:8000/admin/')
        self.stdout.write('\n🚀 Happy testing!')
