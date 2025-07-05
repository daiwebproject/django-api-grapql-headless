import stripe
from django.conf import settings
from oscar.core.loading import get_model

stripe.api_key = settings.STRIPE_SECRET_KEY

Order = get_model('order', 'Order')
PaymentEvent = get_model('order', 'PaymentEvent')
PaymentEventType = get_model('order', 'PaymentEventType')

class PaymentService:
    
    @staticmethod
    def process_stripe_payment(order, stripe_token):
        """Process Stripe payment"""
        try:
            # Create Stripe charge
            charge = stripe.Charge.create(
                amount=int(order.total_incl_tax * 100),  # Convert to cents
                currency='vnd',
                source=stripe_token,
                description=f'Order #{order.number}',
                metadata={
                    'order_id': order.id,
                    'order_number': order.number,
                }
            )
            
            # Record payment event
            event_type, _ = PaymentEventType.objects.get_or_create(
                name='Paid',
                code='paid'
            )
            
            PaymentEvent.objects.create(
                order=order,
                amount=order.total_incl_tax,
                event_type=event_type,
                reference=charge.id
            )
            
            return {
                'success': True,
                'payment_id': charge.id,
                'status': charge.status,
                'errors': []
            }
            
        except stripe.error.CardError as e:
            return {
                'success': False,
                'payment_id': None,
                'status': 'failed',
                'errors': [str(e)]
            }
        except Exception as e:
            return {
                'success': False,
                'payment_id': None,
                'status': 'failed',
                'errors': [str(e)]
            }
    
    @staticmethod
    def process_paypal_payment(order, paypal_order_id):
        """Process PayPal payment"""
        # Implementation for PayPal
        # This would involve PayPal SDK calls
        pass
    
    @staticmethod
    def process_cod_payment(order):
        """Process Cash on Delivery"""
        try:
            event_type, _ = PaymentEventType.objects.get_or_create(
                name='Cash on Delivery',
                code='cod'
            )
            
            PaymentEvent.objects.create(
                order=order,
                amount=order.total_incl_tax,
                event_type=event_type,
                reference=f'COD-{order.number}'
            )
            
            return {
                'success': True,
                'payment_id': f'COD-{order.number}',
                'status': 'pending',
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'payment_id': None,
                'status': 'failed',
                'errors': [str(e)]
            }