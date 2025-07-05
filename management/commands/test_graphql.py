from django.core.management.base import BaseCommand
from graphene.test import Client
from api.schema import schema
import json

class Command(BaseCommand):
    help = 'Test GraphQL endpoints'
    
    def handle(self, *args, **options):
        self.stdout.write('🧪 Testing GraphQL endpoints...')
        
        client = Client(schema)
        
        # Test 1: Query products
        self.stdout.write('\n1️⃣ Testing products query...')
        products_query = '''
            query {
                products {
                    id
                    title
                    slug
                    price
                }
            }
        '''
        
        result = client.execute(products_query)
        
        if result.get('errors'):
            self.stdout.write(
                self.style.ERROR(f'❌ Products query failed: {result["errors"]}')
            )
        else:
            products_count = len(result['data']['products'])
            self.stdout.write(
                self.style.SUCCESS(f'✅ Products query successful! Found {products_count} products.')
            )
            
            # Show first product if exists
            if products_count > 0:
                first_product = result['data']['products'][0]
                self.stdout.write(f'   📦 Sample product: {first_product["title"]} - {first_product["price"]} VND')
        
        # Test 2: Query categories
        self.stdout.write('\n2️⃣ Testing categories query...')
        categories_query = '''
            query {
                categories {
                    id
                    name
                    slug
                }
            }
        '''
        
        result = client.execute(categories_query)
        
        if result.get('errors'):
            self.stdout.write(
                self.style.ERROR(f'❌ Categories query failed: {result["errors"]}')
            )
        else:
            categories_count = len(result['data']['categories'])
            self.stdout.write(
                self.style.SUCCESS(f'✅ Categories query successful! Found {categories_count} categories.')
            )
            
            # Show categories
            if categories_count > 0:
                for category in result['data']['categories']:
                    self.stdout.write(f'   📁 {category["name"]} ({category["slug"]})')
        
        # Test 3: Query specific product
        self.stdout.write('\n3️⃣ Testing specific product query...')
        product_query = '''
            query {
                product(slug: "iphone-15") {
                    id
                    title
                    slug
                    price
                    description
                }
            }
        '''
        
        result = client.execute(product_query)
        
        if result.get('errors'):
            self.stdout.write(
                self.style.ERROR(f'❌ Product query failed: {result["errors"]}')
            )
        else:
            product = result['data']['product']
            if product:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Product query successful!')
                )
                self.stdout.write(f'   📱 {product["title"]} - {product["price"]} VND')
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  Product not found (this is normal if sample data wasn\'t created)')
                )
        
        # Test 4: Schema introspection
        self.stdout.write('\n4️⃣ Testing schema introspection...')
        introspection_query = '''
            query IntrospectionQuery {
                __schema {
                    types {
                        name
                        kind
                    }
                }
            }
        '''
        
        result = client.execute(introspection_query)
        
        if result.get('errors'):
            self.stdout.write(
                self.style.ERROR(f'❌ Schema introspection failed: {result["errors"]}')
            )
        else:
            types_count = len(result['data']['__schema']['types'])
            self.stdout.write(
                self.style.SUCCESS(f'✅ Schema introspection successful! Found {types_count} types.')
            )
            
            # Show custom types
            custom_types = [
                t['name'] for t in result['data']['__schema']['types'] 
                if t['name'] in ['ProductType', 'CategoryType', 'UserType']
            ]
            if custom_types:
                self.stdout.write(f'   🔧 Custom types: {", ".join(custom_types)}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('🎉 GraphQL testing completed!'))
        self.stdout.write('\n📋 Next steps:')
        self.stdout.write('   • Visit http://localhost:8000/graphql/ for interactive testing')
        self.stdout.write('   • Use GraphiQL to explore the schema')
        self.stdout.write('   • Try the queries above in GraphiQL')
        
        # Sample queries for user
        self.stdout.write('\n📝 Sample queries to try in GraphiQL:')
        self.stdout.write('''
        # Get all products with details
        query GetProducts {
          products {
            id
            title
            slug
            price
            description
          }
        }
        
        # Get categories
        query GetCategories {
          categories {
            id
            name
            slug
            description
          }
        }
        
        # Get specific product
        query GetProduct($slug: String!) {
          product(slug: $slug) {
            id
            title
            price
            description
          }
        }
        ''')
        
        self.stdout.write('\n🚀 Happy GraphQL querying!')