import hashlib
import hmac
import urllib.parse
import urllib.request
import random
import string
from datetime import datetime
from django.conf import settings

class VNPayService:
    def __init__(self):
        self.request_data = {}
        self.response_data = {}
    
    def get_payment_url(self, order_id, amount, order_desc, return_url=None, user_ip='127.0.0.1'):
        """Generate VNPAY payment URL"""
        
        # Generate transaction reference
        txn_ref = f"{order_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # VNPAY parameters
        vnp_params = {
            'vnp_Version': settings.VNPAY_CONFIG['VERSION'],
            'vnp_Command': 'pay',
            'vnp_TmnCode': settings.VNPAY_CONFIG['TMN_CODE'],
            'vnp_Amount': str(int(amount * 100)),  # Convert to cents
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': txn_ref,
            'vnp_OrderInfo': order_desc,
            'vnp_OrderType': 'other',
            'vnp_Locale': 'vn',
            'vnp_ReturnUrl': return_url or settings.VNPAY_CONFIG['RETURN_URL'],
            'vnp_IpAddr': user_ip,
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
        }
        
        # Sort and create query string
        sorted_params = sorted(vnp_params.items())
        query_string = urllib.parse.urlencode(sorted_params)
        
        # Create secure hash
        hash_data = query_string
        secure_hash = hmac.new(
            settings.VNPAY_CONFIG['SECRET_KEY'].encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        # Final payment URL
        payment_url = f"{settings.VNPAY_CONFIG['PAYMENT_URL']}?{query_string}&vnp_SecureHash={secure_hash}"
        
        return {
            'payment_url': payment_url,
            'txn_ref': txn_ref,
            'amount': amount,
            'order_desc': order_desc
        }
    
    def validate_response(self, response_data):
        """Validate VNPAY response"""
        
        # Extract secure hash
        vnp_secure_hash = response_data.get('vnp_SecureHash', '')
        
        # Remove hash from data for validation
        validate_data = {k: v for k, v in response_data.items() if k != 'vnp_SecureHash'}
        
        # Sort and create query string
        sorted_params = sorted(validate_data.items())
        query_string = urllib.parse.urlencode(sorted_params)
        
        # Create secure hash
        hash_data = query_string
        secure_hash = hmac.new(
            settings.VNPAY_CONFIG['SECRET_KEY'].encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        # Validate
        is_valid = secure_hash == vnp_secure_hash
        
        return {
            'is_valid': is_valid,
            'transaction_status': response_data.get('vnp_TransactionStatus'),
            'txn_ref': response_data.get('vnp_TxnRef'),
            'amount': int(response_data.get('vnp_Amount', 0)) / 100,
            'response_code': response_data.get('vnp_ResponseCode'),
            'order_info': response_data.get('vnp_OrderInfo'),
        }

