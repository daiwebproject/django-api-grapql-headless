import graphene
from graphene_django import DjangoObjectType
from oscar.core.loading import get_model

Basket = get_model('basket', 'Basket')
Line = get_model('basket', 'Line')

class BasketLineType(DjangoObjectType):
    product = graphene.Field('api.types.product.ProductType')
    line_total = graphene.String()
    
    class Meta:
        model = Line
        fields = ('id', 'quantity', 'price_incl_tax')
    
    def resolve_line_total(self, info):
        return str(self.line_price_incl_tax)

class BasketType(DjangoObjectType):
    lines = graphene.List(BasketLineType)
    total = graphene.String()
    num_items = graphene.Int()
    
    class Meta:
        model = Basket
        fields = ('id', 'status', 'date_created')
    
    def resolve_lines(self, info):
        return self.lines.all()
    
    def resolve_total(self, info):
        return str(self.total_incl_tax)
    
    def resolve_num_items(self, info):
        return self.num_items