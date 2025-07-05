import graphene
from api.types.order import OrderType
from api.types.payment import PaymentMethodInput, PaymentResult
from api.utils.permissions import login_required
from api.services.payment import PaymentService
from oscar.core.loading import get_model
from oscar.apps.order.utils import OrderCreator

class ShippingAddressInput(graphene.InputObjectType):
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    line1 = graphene.String(required=True)
    line4 = graphene.String(required=True)
    postcode = graphene.String(required=True)

class CreateOrderWithPayment(graphene.Mutation):
    class Arguments:
        shipping_address = ShippingAddressInput(required=True)
        payment_method = PaymentMethodInput(required=True)
    
    order = graphene.Field(OrderType)
    payment_result = graphene.Field(PaymentResult)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @login_required
    def mutate(self, info, shipping_address, payment_method):
        user = info.context.user
        Basket = get_model('basket', 'Basket')
        ShippingAddress = get_model('order', 'ShippingAddress')

        try:
            basket = Basket.objects.get(owner=user, status=Basket.OPEN)
            
            if basket.is_empty:
                return CreateOrderWithPayment(
                    order=None,
                    payment_result=None,
                    success=False,
                    errors=["Basket is empty"]
                )
            
            shipping_addr = ShippingAddress(
                first_name=shipping_address.first_name,
                last_name=shipping_address.last_name,
                line1=shipping_address.line1,
                line4=shipping_address.line4,
                postcode=shipping_address.postcode,
            )
            
            order_creator = OrderCreator()
            order = order_creator.create_order_model(
                user=user,
                basket=basket,
                shipping_address=shipping_addr,
            )
            
            # Payment handling
            payment_result = None
            if payment_method.type == 'stripe' and payment_method.stripe_token:
                payment_result = PaymentService.process_stripe_payment(order, payment_method.stripe_token)
            elif payment_method.type == 'paypal' and payment_method.paypal_order_id:
                payment_result = PaymentService.process_paypal_payment(order, payment_method.paypal_order_id)
            elif payment_method.type == 'cod':
                payment_result = PaymentService.process_cod_payment(order)
            
            if payment_result and payment_result['success']:
                order.set_status('Being processed')
            else:
                order.set_status('Payment failed')
            
            return CreateOrderWithPayment(
                order=order,
                payment_result=PaymentResult(**payment_result) if payment_result else None,
                success=payment_result.get('success', False),
                errors=payment_result.get('errors', ['Payment processing failed'])
            )
        except Exception as e:
            return CreateOrderWithPayment(
                order=None,
                payment_result=None,
                success=False,
                errors=[str(e)]
            )

class OrderMutation(graphene.ObjectType):
    create_order_with_payment = CreateOrderWithPayment.Field()
