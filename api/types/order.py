import graphene
from graphene_django import DjangoObjectType
from oscar.core.loading import get_model

Order = get_model('order', 'Order')
OrderLine = get_model('order', 'Line')
ShippingAddress = get_model('order', 'ShippingAddress')

class ShippingAddressType(DjangoObjectType):
    class Meta:
        model = ShippingAddress
        fields = ('id', 'first_name', 'last_name', 'line1', 'line2', 
                 'line4', 'state', 'postcode', 'country')

class OrderLineType(DjangoObjectType):
    product = graphene.Field('api.types.product.ProductType')
    line_total = graphene.String()
    
    class Meta:
        model = OrderLine
        fields = ('id', 'title', 'quantity', 'unit_price_incl_tax')
    
    def resolve_line_total(self, info):
        return str(self.line_price_incl_tax)

class OrderType(DjangoObjectType):
    lines = graphene.List(OrderLineType)
    shipping_address = graphene.Field(ShippingAddressType)
    total = graphene.String()
    
    class Meta:
        model = Order
        fields = ('id', 'number', 'status', 'date_placed')
    
    def resolve_lines(self, info):
        return self.lines.all()
    
    def resolve_total(self, info):
        return str(self.total_incl_tax)