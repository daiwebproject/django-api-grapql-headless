import graphene
from api.types.basket import BasketType
from api.utils.permissions import login_required
from oscar.core.loading import get_model

Basket = get_model('basket', 'Basket')
Product = get_model('catalogue', 'Product')

class AddToBasket(graphene.Mutation):
    class Arguments:
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)
    
    basket = graphene.Field(BasketType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @login_required
    def mutate(self, info, product_id, quantity):
        user = info.context.user
        
        try:
            product = Product.objects.get(id=product_id)
            basket, created = Basket.objects.get_or_create(
                owner=user,
                status=Basket.OPEN
            )
            
            # Add product to basket
            basket.add_product(product, quantity=quantity)
            
            return AddToBasket(basket=basket, success=True, errors=[])
        except Product.DoesNotExist:
            return AddToBasket(basket=None, success=False, errors=["Product not found"])
        except Exception as e:
            return AddToBasket(basket=None, success=False, errors=[str(e)])

class UpdateBasketLine(graphene.Mutation):
    class Arguments:
        line_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)
    
    basket = graphene.Field(BasketType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @login_required
    def mutate(self, info, line_id, quantity):
        user = info.context.user
        
        try:
            basket = Basket.objects.get(owner=user, status=Basket.OPEN)
            line = basket.lines.get(id=line_id)
            
            if quantity <= 0:
                line.delete()
            else:
                line.quantity = quantity
                line.save()
            
            return UpdateBasketLine(basket=basket, success=True, errors=[])
        except Exception as e:
            return UpdateBasketLine(basket=None, success=False, errors=[str(e)])

class BasketMutation:
    add_to_basket = AddToBasket.Field()
    update_basket_line = UpdateBasketLine.Field()