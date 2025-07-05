# api/mutations/payment.py
import graphene
from django.utils import timezone
from payments.vnpay import VNPayService
from payments.models import PaymentTransaction
from booking.models import Booking, BookingHistory
from api.types.payment import VNPayCallbackResult

class ProcessVNPayCallback(graphene.Mutation):
    class Arguments:
        vnp_amount = graphene.String(required=True)
        vnp_bank_code = graphene.String()
        vnp_bank_tran_no = graphene.String()
        vnp_card_type = graphene.String()
        vnp_order_info = graphene.String()
        vnp_pay_date = graphene.String()
        vnp_response_code = graphene.String(required=True)
        vnp_tmn_code = graphene.String()
        vnp_transaction_no = graphene.String()
        vnp_transaction_status = graphene.String(required=True)
        vnp_txn_ref = graphene.String(required=True)
        vnp_secure_hash = graphene.String(required=True)
    
    result = graphene.Field(VNPayCallbackResult)
    
    def mutate(self, info, **kwargs):
        vnpay = VNPayService()
        
        # Validate response
        validation_result = vnpay.validate_response(kwargs)
        
        if not validation_result['is_valid']:
            return ProcessVNPayCallback(
                result=VNPayCallbackResult(
                    success=False,
                    transaction_status='failed',
                    message='Invalid signature'
                )
            )
        
        try:
            # Find payment transaction
            txn_ref = validation_result['txn_ref']
            payment_transaction = PaymentTransaction.objects.get(
                gateway_transaction_id=txn_ref
            )
            
            # Update payment transaction
            payment_transaction.gateway_response_code = kwargs['vnp_response_code']
            payment_transaction.gateway_response_message = kwargs.get('vnp_order_info', '')
            payment_transaction.gateway_transaction_id = kwargs.get('vnp_transaction_no', txn_ref)
            
            booking = payment_transaction.booking
            
            # Process based on transaction status
            if kwargs['vnp_transaction_status'] == '00':  # Success
                payment_transaction.status = 'success'
                payment_transaction.completed_at = timezone.now()
                
                booking.payment_status = 'paid'
                booking.status = 'confirmed'
                booking.payment_method = 'vnpay'
                booking.payment_reference = payment_transaction.gateway_transaction_id
                
                # Create booking history
                BookingHistory.objects.create(
                    booking=booking,
                    previous_status='pending',
                    new_status='confirmed',
                    notes='Payment successful via VNPAY'
                )
                
                message = 'Payment successful'
                
            else:  # Failed
                payment_transaction.status = 'failed'
                booking.payment_status = 'failed'
                
                # Create booking history
                BookingHistory.objects.create(
                    booking=booking,
                    previous_status=booking.status,
                    new_status=booking.status,
                    notes=f'Payment failed via VNPAY. Code: {kwargs["vnp_response_code"]}'
                )
                
                message = 'Payment failed'
            
            payment_transaction.save()
            booking.save()
            
            return ProcessVNPayCallback(
                result=VNPayCallbackResult(
                    success=kwargs['vnp_transaction_status'] == '00',
                    transaction_status=kwargs['vnp_transaction_status'],
                    booking_id=str(booking.booking_id),
                    amount=validation_result['amount'],
                    message=message
                )
            )
            
        except PaymentTransaction.DoesNotExist:
            return ProcessVNPayCallback(
                result=VNPayCallbackResult(
                    success=False,
                    transaction_status='failed',
                    message='Payment transaction not found'
                )
            )
        except Exception as e:
            return ProcessVNPayCallback(
                result=VNPayCallbackResult(
                    success=False,
                    transaction_status='failed',
                    message=str(e)
                )
            )

class PaymentMutation:
    process_vnpay_callback = ProcessVNPayCallback.Field()