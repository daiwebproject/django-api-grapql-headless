# Payment Models
from django.db import models
from booking.models import Booking

class PaymentTransaction(models.Model):
    PAYMENT_METHODS = [
        ('vnpay', 'VNPAY'),
        ('momo', 'MoMo'),
        ('zalopay', 'ZaloPay'),
        ('cash', 'Cash'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Basic info
    transaction_id = models.CharField(max_length=100, unique=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payment_transactions')
    
    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='VND')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Gateway specific
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response_code = models.CharField(max_length=10, blank=True)
    gateway_response_message = models.TextField(blank=True)
    
    # URLs
    payment_url = models.URLField(blank=True)
    return_url = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.booking.booking_id}"