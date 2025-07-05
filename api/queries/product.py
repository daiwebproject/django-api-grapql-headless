import graphene
from graphene_django import DjangoListField
from django.db.models import Q
from oscar.core.loading import get_model
from api.types.product import ProductType, CategoryType
from api.utils.pagination import PaginationInput, SortInput, create_paginated_type, paginate_queryset

Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')

# Create paginated types
PaginatedProductType = create_paginated_type(ProductType, "Product")

class ProductFilterInput(graphene.InputObjectType):
    search = graphene.String()
    category_slug = graphene.String()
    min_price = graphene.Float()
    max_price = graphene.Float()
    in_stock = graphene.Boolean()

class ProductQuery:
    # Basic queries (keeping for backward compatibility)
    products = DjangoListField(ProductType)
    product = graphene.Field(ProductType, slug=graphene.String())
    product_by_id = graphene.Field(ProductType, id=graphene.ID())
    categories = DjangoListField(CategoryType)
    
    # Paginated and filtered queries
    products_paginated = graphene.Field(
        PaginatedProductType,
        filters=ProductFilterInput(),
        pagination=PaginationInput(),
        sort=SortInput()
    )
    
    def resolve_products(self, info, **kwargs):
        return Product.objects.filter(structure='standalone')
    
    def resolve_product(self, info, slug):
        try:
            return Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return None
    
    def resolve_product_by_id(self, info, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None
    
    def resolve_categories(self, info):
        return Category.objects.all()
    
    def resolve_products_paginated(self, info, filters=None, pagination=None, sort=None):
        queryset = Product.objects.filter(structure='standalone')
        
        # Apply filters
        if filters:
            if filters.get('search'):
                search_query = filters['search']
                queryset = queryset.filter(
                    Q(title__icontains=search_query) |
                    Q(description__icontains=search_query)
                )
            
            if filters.get('category_slug'):
                try:
                    category = Category.objects.get(slug=filters['category_slug'])
                    queryset = queryset.filter(categories=category)
                except Category.DoesNotExist:
                    pass
            
            if filters.get('min_price') is not None:
                queryset = queryset.filter(stockrecords__price__gte=filters['min_price'])
            
            if filters.get('max_price') is not None:
                queryset = queryset.filter(stockrecords__price__lte=filters['max_price'])
            
            if filters.get('in_stock') is not None:
                if filters['in_stock']:
                    queryset = queryset.filter(stockrecords__num_in_stock__gt=0)
                else:
                    queryset = queryset.filter(stockrecords__num_in_stock__lte=0)
        
        # Apply sorting
        if sort:
            sort_field = sort.get('field', 'date_created')
            sort_direction = sort.get('direction', 'DESC')
            
            sort_mapping = {
                'title': 'title',
                'price': 'stockrecords__price',
                'date_created': 'date_created',
                'popularity': '-num_in_stock',  # Example
            }
            
            if sort_field in sort_mapping:
                order_field = sort_mapping[sort_field]
                if sort_direction == 'DESC':
                    order_field = f'-{order_field.lstrip("-")}'
                queryset = queryset.order_by(order_field)
        
        # Remove duplicates
        queryset = queryset.distinct()
        
        # Apply pagination
        page = pagination.get('page', 1) if pagination else 1
        page_size = pagination.get('page_size', 20) if pagination else 20
        
        return paginate_queryset(queryset, page, page_size)