# api/types/product.py
import graphene
from graphene_django import DjangoObjectType
from oscar.core.loading import get_model

# Oscar 4.0 models
Product = get_model('catalogue', 'Product')
ProductClass = get_model('catalogue', 'ProductClass')
Category = get_model('catalogue', 'Category')
ProductImage = get_model('catalogue', 'ProductImage')
ProductAttribute = get_model('catalogue', 'ProductAttribute')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
StockRecord = get_model('partner', 'StockRecord')

class ProductImageType(DjangoObjectType):
    url = graphene.String()
    
    class Meta:
        model = ProductImage
        fields = ('id', 'original', 'caption', 'display_order')
    
    def resolve_url(self, info):
        if self.original:
            return self.original.url
        return None

class CategoryType(DjangoObjectType):
    children = graphene.List(lambda: CategoryType)
    parent = graphene.Field(lambda: CategoryType)
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image', 'is_public')
    
    def resolve_children(self, info):
        return self.get_children().filter(is_public=True)

class ProductClassType(DjangoObjectType):
    class Meta:
        model = ProductClass
        fields = ('id', 'name', 'slug', 'requires_shipping', 'track_stock')

class ProductAttributeValueType(DjangoObjectType):
    attribute_name = graphene.String()
    
    class Meta:
        model = ProductAttributeValue
        fields = ('id', 'value_text', 'value_integer', 'value_boolean', 
                 'value_float', 'value_richtext', 'value_date', 'value_datetime')
    
    def resolve_attribute_name(self, info):
        return self.attribute.name

class StockRecordType(DjangoObjectType):
    availability = graphene.String()
    
    class Meta:
        model = StockRecord
        fields = ('id', 'price', 'num_in_stock', 'low_stock_threshold')
    
    def resolve_availability(self, info):
        if self.num_in_stock > 0:
            return f"{self.num_in_stock} in stock"
        return "Out of stock"

class ProductType(DjangoObjectType):
    images = graphene.List(ProductImageType)
    categories = graphene.List(CategoryType)
    price = graphene.String()
    availability = graphene.String()
    attributes = graphene.List(ProductAttributeValueType)
    stock_records = graphene.List(StockRecordType)
    
    class Meta:
        model = Product
        fields = ('id', 'title', 'slug', 'description', 'product_class', 
                 'date_created', 'date_updated', 'is_public', 'structure')
    
    def resolve_images(self, info):
        return self.images.all().order_by('display_order')
    
    def resolve_categories(self, info):
        return self.categories.filter(is_public=True)
    
    def resolve_price(self, info):
        stockrecord = self.stockrecords.first()
        if stockrecord and stockrecord.price:
            return f"{stockrecord.price:,.0f}"
        return "0"
    
    def resolve_availability(self, info):
        stockrecord = self.stockrecords.first()
        if stockrecord:
            if stockrecord.num_in_stock > 0:
                return f"{stockrecord.num_in_stock} in stock"
            else:
                return "Out of stock"
        return "Not available"
    
    def resolve_attributes(self, info):
        return self.attribute_values.all()
    
    def resolve_stock_records(self, info):
        return self.stockrecords.all()