import graphene
from graphene_django import DjangoObjectType
from payments.models import PaymentTransaction

class PaymentTransactionType(DjangoObjectType):
    amount_formatted = graphene.String()
    status_display = graphene.String()
    
    class Meta:
        model = PaymentTransaction
        fields = ('id', 'transaction_id', 'booking', 'payment_method', 'amount',
                 'currency', 'status', 'gateway_transaction_id', 'payment_url',
                 'created_at', 'updated_at', 'completed_at')
    
    def resolve_amount_formatted(self, info):
        return f"{self.amount:,.0f} {self.currency}"
    
    def resolve_status_display(self, info):
        return self.get_status_display()

class PaymentResult(graphene.ObjectType):
    success = graphene.Boolean()
    payment_url = graphene.String()
    transaction_id = graphene.String()
    message = graphene.String()
    errors = graphene.List(graphene.String)

class VNPayCallbackResult(graphene.ObjectType):
    success = graphene.Boolean()
    transaction_status = graphene.String()
    booking_id = graphene.String()
    amount = graphene.Float()
    message = graphene.String()

class PaymentMethodInput(graphene.InputObjectType):
    type = graphene.String(required=True)  # ví dụ: 'vnpay', 'cod', 'paypal'
    stripe_token = graphene.String()       # không cần nếu chỉ dùng VNPAY
    paypal_order_id = graphene.String()    # không cần nếu chỉ dùng VNPAY
    vnpay_return_url = graphene.String()   # bắt buộc với VNPAY
