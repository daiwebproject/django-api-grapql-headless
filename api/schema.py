import graphene
from api.queries.product import ProductQuery
from api.queries.basket import BasketQuery
from api.queries.booking import BookingQuery
from api.mutations.auth import AuthMutation
from api.mutations.basket import BasketMutation
from api.mutations.order import OrderMutation
from api.mutations.upload import UploadMutation
from api.mutations.booking import BookingMutation
from api.mutations.payment import PaymentMutation
from api.subscriptions.order import OrderSubscription

class Query(
    ProductQuery, 
     
    BasketQuery, 
    BookingQuery,
    graphene.ObjectType
):
    pass

class Mutation(
    AuthMutation, 
    BasketMutation, 
    OrderMutation, 
    UploadMutation,
    BookingMutation,
    PaymentMutation,
    graphene.ObjectType
):
    pass

class Subscription(OrderSubscription, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)