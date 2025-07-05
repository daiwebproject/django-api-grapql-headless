import graphene
from api.types.order import OrderType
from oscar.core.loading import get_model

Order = get_model('order', 'Order')

class OrderSubscription(graphene.ObjectType):
    order_status_updated = graphene.Field(
        OrderType,
        order_id=graphene.ID(required=True)
    )
    
    user_orders_updated = graphene.Field(
        OrderType,
        user_id=graphene.ID(required=True)
    )
    
    def resolve_order_status_updated(self, info, order_id):
        return Order.objects.filter(id=order_id).first()
    
    def resolve_user_orders_updated(self, info, user_id):
        return Order.objects.filter(user_id=user_id).first()

# Order Status Update Signal
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    """Send real-time updates when order status changes"""
    channel_layer = get_channel_layer()
    
    # Notify specific order subscription
    async_to_sync(channel_layer.group_send)(
        f"order_{instance.id}",
        {
            'type': 'order_update',
            'order_id': instance.id,
            'status': instance.status
        }
    )
    
    # Notify user's orders subscription
    if instance.user:
        async_to_sync(channel_layer.group_send)(
            f"user_orders_{instance.user.id}",
            {
                'type': 'order_update',
                'order_id': instance.id,
                'user_id': instance.user.id,
                'status': instance.status
            }
        )