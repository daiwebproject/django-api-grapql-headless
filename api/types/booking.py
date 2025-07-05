import graphene
from graphene_django import DjangoObjectType
from booking.models import ServiceCategory, Service, StaffSchedule, TimeSlot, Booking, BookingHistory
from api.types.user import UserType

class ServiceCategoryType(DjangoObjectType):
    services_count = graphene.Int()
    
    class Meta:
        model = ServiceCategory
        fields = ('id', 'name', 'slug', 'description', 'image', 'is_active', 'created_at')
    
    def resolve_services_count(self, info):
        return self.services.filter(is_active=True).count()

class ServiceType(DjangoObjectType):
    available_staff = graphene.List(UserType)
    average_rating = graphene.Float()
    total_bookings = graphene.Int()
    
    class Meta:
        model = Service
        fields = ('id', 'name', 'slug', 'category', 'description', 'duration_minutes', 
                 'price', 'is_active', 'advance_booking_days', 'min_advance_hours',
                 'max_bookings_per_day', 'image', 'created_at', 'updated_at')
    
    def resolve_available_staff(self, info):
        return self.available_staff.filter(is_active=True)
    
    def resolve_average_rating(self, info):
        # Implement rating logic if needed
        return 4.5
    
    def resolve_total_bookings(self, info):
        return self.bookings.filter(status__in=['confirmed', 'completed']).count()

class StaffScheduleType(DjangoObjectType):
    weekday_display = graphene.String()
    
    class Meta:
        model = StaffSchedule
        fields = ('id', 'staff', 'weekday', 'start_time', 'end_time', 'is_available')
    
    def resolve_weekday_display(self, info):
        return self.get_weekday_display()

class TimeSlotType(DjangoObjectType):
    formatted_datetime = graphene.String()
    is_past = graphene.Boolean()
    
    class Meta:
        model = TimeSlot
        fields = ('id', 'service', 'staff', 'start_datetime', 'end_datetime', 'is_available')
    
    def resolve_formatted_datetime(self, info):
        return self.start_datetime.strftime('%Y-%m-%d %H:%M')
    
    def resolve_is_past(self, info):
        from django.utils import timezone
        return self.start_datetime < timezone.now()

class BookingType(DjangoObjectType):
    duration_minutes = graphene.Int()
    can_cancel = graphene.Boolean()
    can_reschedule = graphene.Boolean()
    time_until_appointment = graphene.String()
    
    class Meta:
        model = Booking
        fields = ('id', 'booking_id', 'customer', 'service', 'staff', 'start_datetime',
                 'end_datetime', 'status', 'payment_status', 'customer_name',
                 'customer_email', 'customer_phone', 'notes', 'original_price',
                 'final_price', 'discount_amount', 'payment_method',
                 'payment_reference', 'created_at', 'updated_at')
    
    def resolve_duration_minutes(self, info):
        return self.duration_minutes
    
    def resolve_can_cancel(self, info):
        from django.utils import timezone
        from datetime import timedelta
        
        # Can cancel if booking is at least 2 hours away and not already cancelled/completed
        if self.status in ['cancelled', 'completed', 'no_show']:
            return False
        
        now = timezone.now()
        return self.start_datetime > now + timedelta(hours=2)
    
    def resolve_can_reschedule(self, info):
        # Similar logic to cancellation
        return self.can_cancel and self.status in ['pending', 'confirmed']
    
    def resolve_time_until_appointment(self, info):
        from django.utils import timezone
        
        now = timezone.now()
        if self.start_datetime <= now:
            return "Started or passed"
        
        diff = self.start_datetime - now
        hours = diff.total_seconds() / 3600
        
        if hours < 1:
            return f"{int(diff.total_seconds() / 60)} minutes"
        elif hours < 24:
            return f"{int(hours)} hours"
        else:
            return f"{int(hours / 24)} days"

class BookingHistoryType(DjangoObjectType):
    class Meta:
        model = BookingHistory
        fields = ('id', 'booking', 'previous_status', 'new_status', 'changed_by', 'notes', 'created_at')