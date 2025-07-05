from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from oscar.core.loading import get_model
import uuid

User = get_user_model()
Product = get_model('catalogue', 'Product')

class ServiceCategory(models.Model):
    """Categories for services (e.g., Consultation, Treatment, etc.)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='service_categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Service Categories"
    
    def __str__(self):
        return self.name

class Service(models.Model):
    """Services that can be booked"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Availability settings
    is_active = models.BooleanField(default=True)
    advance_booking_days = models.PositiveIntegerField(default=30, help_text="How many days in advance can be booked")
    min_advance_hours = models.PositiveIntegerField(default=2, help_text="Minimum hours in advance")
    max_bookings_per_day = models.PositiveIntegerField(default=10)
    
    # Staff assignment
    available_staff = models.ManyToManyField(User, related_name='available_services', blank=True)
    
    # SEO & Media
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.duration_minutes}min)"

class StaffSchedule(models.Model):
    """Staff working hours and availability"""
    WEEKDAYS = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
    
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['staff', 'weekday']
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.get_weekday_display()}"

class TimeSlot(models.Model):
    """Available time slots for booking"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='time_slots')
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_slots')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['staff', 'start_datetime', 'end_datetime']
        ordering = ['start_datetime']
    
    def __str__(self):
        return f"{self.service.name} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"

class Booking(models.Model):
    """Main booking model"""
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]
    
    # Basic info
    booking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_bookings')
    
    # Timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Customer details
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    notes = models.TextField(blank=True, help_text="Special requests or notes")
    
    # Pricing
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=200, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.customer_name}"
    
    @property
    def duration_minutes(self):
        return (self.end_datetime - self.start_datetime).total_seconds() / 60

class BookingHistory(models.Model):
    """Track booking status changes"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='history')
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Booking Histories"