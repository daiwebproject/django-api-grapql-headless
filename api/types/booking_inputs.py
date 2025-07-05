# api/types/booking_inputs.py
import graphene
from datetime import datetime

class ServiceFilterInput(graphene.InputObjectType):
    category_slug = graphene.String()
    min_price = graphene.Float()
    max_price = graphene.Float()
    duration_min = graphene.Int()
    duration_max = graphene.Int()
    staff_id = graphene.ID()

class BookingCreateInput(graphene.InputObjectType):
    service_id = graphene.ID(required=True)
    staff_id = graphene.ID(required=True)
    start_datetime = graphene.DateTime(required=True)
    customer_name = graphene.String(required=True)
    customer_email = graphene.String(required=True)
    customer_phone = graphene.String(required=True)
    notes = graphene.String()

class BookingUpdateInput(graphene.InputObjectType):
    booking_id = graphene.String(required=True)
    start_datetime = graphene.DateTime()
    customer_name = graphene.String()
    customer_email = graphene.String()
    customer_phone = graphene.String()
    notes = graphene.String()

class TimeSlotFilterInput(graphene.InputObjectType):
    service_id = graphene.ID()
    staff_id = graphene.ID()
    date_from = graphene.Date()
    date_to = graphene.Date()
    available_only = graphene.Boolean(default_value=True)