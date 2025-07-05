import graphene
from api.types.basket import BasketType
from api.utils.permissions import login_required
from oscar.core.loading import get_model

Basket = get_model('basket', 'Basket')

class BasketQuery:
    my_basket = graphene.Field(BasketType)
    
    @login_required
    def resolve_my_basket(self, info):
        user = info.context.user
        basket, created = Basket.objects.get_or_create(
            owner=user,
            status=Basket.OPEN
        )
        return basket