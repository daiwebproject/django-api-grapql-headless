import graphene
from django.utils import timezone
from datetime import datetime, timedelta, date
from booking.models import ServiceCategory, Service, TimeSlot, Booking, StaffSchedule
from api.types.booking import (
    ServiceCategoryType, ServiceType, TimeSlotType, BookingType, StaffScheduleType
)
from api.types.booking_inputs import ServiceFilterInput, TimeSlotFilterInput
from api.utils.permissions import login_required
from api.utils.pagination import create_paginated_type, paginate_queryset, PaginationInput

# Create paginated types
PaginatedServiceType = create_paginated_type(ServiceType, "Service")
PaginatedBookingType = create_paginated_type(BookingType, "Booking")
PaginatedTimeSlotType = create_paginated_type(TimeSlotType, "TimeSlot")

class BookingQuery:
    # Service categories
    service_categories = graphene.List(ServiceCategoryType)
    service_category = graphene.Field(ServiceCategoryType, slug=graphene.String())
    
    # Services
    services = graphene.Field(
        PaginatedServiceType,
        filters=ServiceFilterInput(),
        pagination=PaginationInput()
    )
    service = graphene.Field(ServiceType, slug=graphene.String())
    service_by_id = graphene.Field(ServiceType, id=graphene.ID())
    
    # Time slots
    available_time_slots = graphene.Field(
        PaginatedTimeSlotType,
        filters=TimeSlotFilterInput(),
        pagination=PaginationInput()
    )
    
    # Staff schedules
    staff_schedules = graphene.List(StaffScheduleType, staff_id=graphene.ID())
    
    # User bookings
    my_bookings = graphene.Field(
        PaginatedBookingType,
        status=graphene.String(),
        pagination=PaginationInput()
    )
    booking_by_id = graphene.Field(BookingType, booking_id=graphene.String())
    
    # Admin queries (staff only)
    all_bookings = graphene.Field(
        PaginatedBookingType,
        date_from=graphene.Date(),
        date_to=graphene.Date(),
        staff_id=graphene.ID(),
        status=graphene.String(),
        pagination=PaginationInput()
    )
    
    def resolve_service_categories(self, info):
        return ServiceCategory.objects.filter(is_active=True).order_by('name')
    
    def resolve_service_category(self, info, slug):
        try:
            return ServiceCategory.objects.get(slug=slug, is_active=True)
        except ServiceCategory.DoesNotExist:
            return None
    
    def resolve_services(self, info, filters=None, pagination=None):
        queryset = Service.objects.filter(is_active=True)
        
        # Apply filters
        if filters:
            if filters.get('category_slug'):
                queryset = queryset.filter(category__slug=filters['category_slug'])
            
            if filters.get('min_price') is not None:
                queryset = queryset.filter(price__gte=filters['min_price'])
            
            if filters.get('max_price') is not None:
                queryset = queryset.filter(price__lte=filters['max_price'])
            
            if filters.get('duration_min'):
                queryset = queryset.filter(duration_minutes__gte=filters['duration_min'])
            
            if filters.get('duration_max'):
                queryset = queryset.filter(duration_minutes__lte=filters['duration_max'])
            
            if filters.get('staff_id'):
                queryset = queryset.filter(available_staff__id=filters['staff_id'])
        
        queryset = queryset.order_by('category__name', 'name')
        
        # Apply pagination
        page = pagination.get('page', 1) if pagination else 1
        page_size = pagination.get('page_size', 20) if pagination else 20
        
        return paginate_queryset(queryset, page, page_size)
    
    def resolve_service(self, info, slug):
        try:
            return Service.objects.get(slug=slug, is_active=True)
        except Service.DoesNotExist:
            return None
    
    def resolve_service_by_id(self, info, id):
        try:
            return Service.objects.get(id=id, is_active=True)
        except Service.DoesNotExist:
            return None
    
    def resolve_available_time_slots(self, info, filters=None, pagination=None):
        now = timezone.now()
        queryset = TimeSlot.objects.filter(
            is_available=True,
            start_datetime__gte=now
        )
        
        # Apply filters
        if filters:
            if filters.get('service_id'):
                queryset = queryset.filter(service_id=filters['service_id'])
            
            if filters.get('staff_id'):
                queryset = queryset.filter(staff_id=filters['staff_id'])
            
            if filters.get('date_from'):
                start_of_day = datetime.combine(filters['date_from'], datetime.min.time())
                queryset = queryset.filter(start_datetime__gte=start_of_day)
            
            if filters.get('date_to'):
                end_of_day = datetime.combine(filters['date_to'], datetime.max.time())
                queryset = queryset.filter(start_datetime__lte=end_of_day)
        
        queryset = queryset.order_by('start_datetime')
        
        # Apply pagination
        page = pagination.get('page', 1) if pagination else 1
        page_size = pagination.get('page_size', 50) if pagination else 50
        
        return paginate_queryset(queryset, page, page_size)
    
    def resolve_staff_schedules(self, info, staff_id=None):
        queryset = StaffSchedule.objects.filter(is_available=True)
        
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        
        return queryset.order_by('staff', 'weekday')
    
    @login_required
    def resolve_my_bookings(self, info, status=None, pagination=None):
        user = info.context.user
        queryset = Booking.objects.filter(customer=user)
        
        if status:
            queryset = queryset.filter(status=status)
        
        queryset = queryset.order_by('-created_at')
        
        # Apply pagination
        page = pagination.get('page', 1) if pagination else 1
        page_size = pagination.get('page_size', 20) if pagination else 20
        
        return paginate_queryset(queryset, page, page_size)
    
    @login_required
    def resolve_booking_by_id(self, info, booking_id):
        user = info.context.user
        
        try:
            return Booking.objects.get(
                booking_id=booking_id,
                customer=user
            )
        except Booking.DoesNotExist:
            return None
    
    @login_required
    def resolve_all_bookings(self, info, date_from=None, date_to=None, 
                           staff_id=None, status=None, pagination=None):
        user = info.context.user
        
        # Check if user is staff
        if not user.is_staff:
            raise GraphQLError("Staff permission required")
        
        queryset = Booking.objects.all()
        
        # Apply filters
        if date_from:
            start_of_day = datetime.combine(date_from, datetime.min.time())
            queryset = queryset.filter(start_datetime__gte=start_of_day)
        
        if date_to:
            end_of_day = datetime.combine(date_to, datetime.max.time())
            queryset = queryset.filter(start_datetime__lte=end_of_day)
        
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        queryset = queryset.order_by('-created_at')
        
        # Apply pagination
        page = pagination.get('page', 1) if pagination else 1
        page_size = pagination.get('page_size', 20) if pagination else 20
        
        return paginate_queryset(queryset, page, page_size)