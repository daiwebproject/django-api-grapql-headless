import graphene
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
from booking.models import Service, Booking, TimeSlot, BookingHistory
from payments.models import PaymentTransaction
from payments.vnpay import VNPayService
from api.types.booking import BookingType
from api.types.payment import PaymentResult
from api.types.booking_inputs import BookingCreateInput, BookingUpdateInput
from api.utils.permissions import login_required

class CreateBooking(graphene.Mutation):
    class Arguments:
        input = BookingCreateInput(required=True)
        payment_method = graphene.String(required=True)
        return_url = graphene.String()
    
    booking = graphene.Field(BookingType)
    payment_result = graphene.Field(PaymentResult)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @login_required
    def mutate(self, info, input, payment_method, return_url=None):
        user = info.context.user
        
        try:
            with transaction.atomic():
                # Validate service
                service = Service.objects.get(id=input.service_id, is_active=True)
                
                # Validate staff
                if input.staff_id:
                    staff = service.available_staff.get(id=input.staff_id)
                else:
                    # Auto-assign available staff
                    available_staff = service.available_staff.filter(is_active=True)
                    if not available_staff:
                        return CreateBooking(
                            booking=None, payment_result=None, 
                            success=False, errors=["No staff available for this service"]
                        )
                    staff = available_staff.first()
                
                # Validate datetime
                start_datetime = input.start_datetime
                end_datetime = start_datetime + timedelta(minutes=service.duration_minutes)
                
                # Check availability
                conflicts = Booking.objects.filter(
                    staff=staff,
                    start_datetime__lt=end_datetime,
                    end_datetime__gt=start_datetime,
                    status__in=['pending', 'confirmed', 'in_progress']
                ).exists()
                
                if conflicts:
                    return CreateBooking(
                        booking=None, payment_result=None,
                        success=False, errors=["Time slot not available"]
                    )
                
                # Create booking
                booking = Booking.objects.create(
                    customer=user,
                    service=service,
                    staff=staff,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    customer_name=input.customer_name,
                    customer_email=input.customer_email,
                    customer_phone=input.customer_phone,
                    notes=input.notes or '',
                    original_price=service.price,
                    final_price=service.price,  # Apply discounts here if needed
                    status='pending'
                )
                
                # Create payment transaction
                if payment_method == 'vnpay':
                    payment_result = self._create_vnpay_payment(booking, return_url)
                elif payment_method == 'cash':
                    payment_result = self._create_cash_payment(booking)
                else:
                    return CreateBooking(
                        booking=None, payment_result=None,
                        success=False, errors=["Unsupported payment method"]
                    )
                
                # Create booking history
                BookingHistory.objects.create(
                    booking=booking,
                    previous_status='',
                    new_status='pending',
                    changed_by=user,
                    notes='Booking created'
                )
                
                return CreateBooking(
                    booking=booking,
                    payment_result=payment_result,
                    success=True,
                    errors=[]
                )
                
        except Service.DoesNotExist:
            return CreateBooking(
                booking=None, payment_result=None,
                success=False, errors=["Service not found"]
            )
        except Exception as e:
            return CreateBooking(
                booking=None, payment_result=None,
                success=False, errors=[str(e)]
            )
    
    def _create_vnpay_payment(self, booking, return_url):
        """Create VNPAY payment"""
        vnpay = VNPayService()
        
        # Generate transaction ID
        transaction_id = f"TXN{booking.booking_id.hex[:8].upper()}"
        
        # Create payment transaction record
        payment_transaction = PaymentTransaction.objects.create(
            transaction_id=transaction_id,
            booking=booking,
            payment_method='vnpay',
            amount=booking.final_price,
            status='pending',
            return_url=return_url or ''
        )
        
        # Get payment URL from VNPAY
        payment_data = vnpay.get_payment_url(
            order_id=str(booking.booking_id),
            amount=float(booking.final_price),
            order_desc=f"Payment for {booking.service.name} - {booking.customer_name}",
            return_url=return_url
        )
        
        # Update payment transaction
        payment_transaction.payment_url = payment_data['payment_url']
        payment_transaction.gateway_transaction_id = payment_data['txn_ref']
        payment_transaction.save()
        
        return PaymentResult(
            success=True,
            payment_url=payment_data['payment_url'],
            transaction_id=transaction_id,
            message="Payment URL generated successfully",
            errors=[]
        )
    
    def _create_cash_payment(self, booking):
        """Create cash payment (for walk-in customers)"""
        transaction_id = f"CASH{booking.booking_id.hex[:8].upper()}"
        
        PaymentTransaction.objects.create(
            transaction_id=transaction_id,
            booking=booking,
            payment_method='cash',
            amount=booking.final_price,
            status='pending'
        )
        
        return PaymentResult(
            success=True,
            payment_url='',
            transaction_id=transaction_id,
            message="Cash payment registered",
            errors=[]
        )

class UpdateBooking(graphene.Mutation):
    class Arguments:
        input = BookingUpdateInput(required=True)
    
    booking = graphene.Field(BookingType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @login_required
    def mutate(self, info, input):
        user = info.context.user
        
        try:
            booking = Booking.objects.get(
                booking_id=input.booking_id,
                customer=user
            )
            
            if not booking.can_reschedule:
                return UpdateBooking(
                    booking=None,
                    success=False,
                    errors=["Booking cannot be rescheduled"]
                )
            
            # Update fields
            old_status = booking.status
            
            if input.start_datetime:
                # Validate new time slot
                new_end = input.start_datetime + timedelta(minutes=booking.service.duration_minutes)
                
                conflicts = Booking.objects.filter(
                    staff=booking.staff,
                    start_datetime__lt=new_end,
                    end_datetime__gt=input.start_datetime,
                    status__in=['pending', 'confirmed', 'in_progress']
                ).exclude(id=booking.id).exists()
                
                if conflicts:
                    return UpdateBooking(
                        booking=None,
                        success=False,
                        errors=["New time slot not available"]
                    )
                
                booking.start_datetime = input.start_datetime
                booking.end_datetime = new_end
            
            if input.customer_name:
                booking.customer_name = input.customer_name
            if input.customer_email:
                booking.customer_email = input.customer_email
            if input.customer_phone:
                booking.customer_phone = input.customer_phone
            if input.notes is not None:
                booking.notes = input.notes
            
            booking.save()
            
            # Create history record
            BookingHistory.objects.create(
                booking=booking,
                previous_status=old_status,
                new_status=booking.status,
                changed_by=user,
                notes='Booking updated by customer'
            )
            
            return UpdateBooking(
                booking=booking,
                success=True,
                errors=[]
            )
            
        except Booking.DoesNotExist:
            return UpdateBooking(
                booking=None,
                success=False,
                errors=["Booking not found"]
            )
        except Exception as e:
            return UpdateBooking(
                booking=None,
                success=False,
                errors=[str(e)]
            )

class CancelBooking(graphene.Mutation):
    class Arguments:
        booking_id = graphene.String(required=True)
        reason = graphene.String()
    
    booking = graphene.Field(BookingType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @login_required
    def mutate(self, info, booking_id, reason=None):
        user = info.context.user
        
        try:
            booking = Booking.objects.get(
                booking_id=booking_id,
                customer=user
            )
            
            if not booking.can_cancel:
                return CancelBooking(
                    booking=None,
                    success=False,
                    errors=["Booking cannot be cancelled"]
                )
            
            old_status = booking.status
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.save()
            
            # Create history record
            BookingHistory.objects.create(
                booking=booking,
                previous_status=old_status,
                new_status='cancelled',
                changed_by=user,
                notes=f'Booking cancelled by customer. Reason: {reason or "No reason provided"}'
            )
            
            # Handle refund if needed
            # TODO: Implement refund logic based on cancellation policy
            
            return CancelBooking(
                booking=booking,
                success=True,
                errors=[]
            )
            
        except Booking.DoesNotExist:
            return CancelBooking(
                booking=None,
                success=False,
                errors=["Booking not found"]
            )
        except Exception as e:
            return CancelBooking(
                booking=None,
                success=False,
                errors=[str(e)]
            )

class BookingMutation:
    create_booking = CreateBooking.Field()
    update_booking = UpdateBooking.Field()
    cancel_booking = CancelBooking.Field()