from django.contrib import admin
from .models import ServiceCategory, Service, StaffSchedule, TimeSlot, Booking, BookingHistory

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'duration_minutes', 'price', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['available_staff']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    list_display = ['staff', 'weekday', 'start_time', 'end_time', 'is_available']
    list_filter = ['weekday', 'is_available']
    ordering = ['staff', 'weekday']

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['service', 'staff', 'start_datetime', 'end_datetime', 'is_available']
    list_filter = ['service', 'staff', 'is_available', 'start_datetime']
    ordering = ['start_datetime']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'customer_name', 'service', 'staff', 'start_datetime', 'status', 'payment_status']
    list_filter = ['status', 'payment_status', 'service', 'staff', 'start_datetime']
    search_fields = ['booking_id', 'customer_name', 'customer_email', 'customer_phone']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ['booking', 'previous_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['previous_status', 'new_status', 'created_at']
    readonly_fields = ['created_at']