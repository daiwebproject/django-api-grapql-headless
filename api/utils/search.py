from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q, F
from oscar.core.loading import get_model

Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')

class ProductSearchEngine:
    @staticmethod
    def search_products(query, filters=None):
        """
        Advanced product search with full-text search and filters
        """
        queryset = Product.objects.filter(structure='standalone')
        
        if query:
            # PostgreSQL full-text search
            search_vector = SearchVector('title', weight='A') + SearchVector('description', weight='B')
            search_query = SearchQuery(query)
            
            queryset = queryset.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank')
        
        # Apply additional filters
        if filters:
            queryset = ProductSearchEngine._apply_filters(queryset, filters)
        
        return queryset
    
    @staticmethod
    def _apply_filters(queryset, filters):
        """Apply various filters to the queryset"""
        
        if filters.get('categories'):
            category_slugs = filters['categories']
            queryset = queryset.filter(categories__slug__in=category_slugs)
        
        if filters.get('price_range'):
            min_price = filters['price_range'].get('min')
            max_price = filters['price_range'].get('max')
            
            if min_price is not None:
                queryset = queryset.filter(stockrecords__price__gte=min_price)
            if max_price is not None:
                queryset = queryset.filter(stockrecords__price__lte=max_price)
        
        if filters.get('availability'):
            if filters['availability'] == 'in_stock':
                queryset = queryset.filter(stockrecords__num_in_stock__gt=0)
            elif filters['availability'] == 'out_of_stock':
                queryset = queryset.filter(stockrecords__num_in_stock__lte=0)
        
        if filters.get('rating_min'):
            # Assuming you have a rating system
            queryset = queryset.filter(reviews__score__gte=filters['rating_min'])
        
        return queryset.distinct()

# Enhanced Filter Input
class AdvancedProductFilterInput(graphene.InputObjectType):
    search = graphene.String()
    categories = graphene.List(graphene.String)
    price_range = graphene.InputObjectType('PriceRangeInput', [
        ('min', graphene.Float()),
        ('max', graphene.Float()),
    ])
    availability = graphene.Enum('AvailabilityFilter', [
        ('IN_STOCK', 'in_stock'),
        ('OUT_OF_STOCK', 'out_of_stock'),
        ('ALL', 'all')
    ])()
    rating_min = graphene.Float()
    brand = graphene.String()
    
class ProductSearchQuery:
    search_products = graphene.Field(
        PaginatedProductType,
        query=graphene.String(),
        filters=AdvancedProductFilterInput(),
        pagination=PaginationInput(),
        sort=SortInput()
    )
    
    def resolve_search_products(self, info, query=None, filters=None, pagination=None, sort=None):
        # Use the search engine
        queryset = ProductSearchEngine.search_products(query, filters)
        
        # Apply sorting if no search query (search has its own ranking)
        if not query and sort:
            # Apply sorting logic
            pass
        
        # Apply pagination
        page = pagination.get('page', 1) if pagination else 1
        page_size = pagination.get('page_size', 20) if pagination else 20
        
        return paginate_queryset(queryset, page, page_size)