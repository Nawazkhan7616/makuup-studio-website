"""
MakuUP Studio — DRF Serializers
Uses plain DRF Serializer (not ModelSerializer) since MongoEngine doesn't
integrate with DRF's ModelSerializer out of the box.
"""
import re
from datetime import date
from rest_framework import serializers


# ──────────────────────────────────────────────
# BOOKING
# ──────────────────────────────────────────────
class BookingCreateSerializer(serializers.Serializer):
    name    = serializers.CharField(max_length=200)
    email   = serializers.EmailField()
    phone   = serializers.CharField(max_length=20, required=False, allow_blank=True)
    service = serializers.ChoiceField(choices=[
        'bridal', 'editorial', 'sangeet', 'engagement',
        'mehendi', 'everyday', 'lessons', 'skincare',
    ])
    date    = serializers.DateField()
    message = serializers.CharField(max_length=2000, required=False, allow_blank=True)

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Please enter your full name.")
        return value.strip()

    def validate_phone(self, value):
        if value:
            cleaned = re.sub(r'[\s\-\(\)\+]', '', value)
            if not cleaned.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits.")
            if len(cleaned) < 7 or len(cleaned) > 15:
                raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def validate_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Booking date cannot be in the past.")
        return str(value)  # store as string "YYYY-MM-DD"


class BookingStatusSerializer(serializers.Serializer):
    STATUS_CHOICES = ('new', 'contacted', 'confirmed')
    status = serializers.ChoiceField(choices=STATUS_CHOICES)


class BookingListSerializer(serializers.Serializer):
    """Serializes a MongoEngine Booking document to dict."""

    @staticmethod
    def serialize(booking):
        return {
            'id': str(booking.id),
            'name': booking.name,
            'email': booking.email,
            'phone': booking.phone or '',
            'service': booking.service,
            'date': booking.date,
            'message': booking.message or '',
            'status': booking.status,
            'created_at': (booking.created_at.isoformat() + 'Z') if booking.created_at else None,
        }

    @classmethod
    def serialize_many(cls, bookings):
        return [cls.serialize(b) for b in bookings]


# ──────────────────────────────────────────────
# TESTIMONIAL
# ──────────────────────────────────────────────
class TestimonialSerializer(serializers.Serializer):
    name     = serializers.CharField(max_length=200)
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    service  = serializers.CharField(max_length=100, required=False, allow_blank=True)
    quote    = serializers.CharField(max_length=2000)
    rating   = serializers.IntegerField(min_value=1, max_value=5, default=5)
    avatar_bg = serializers.CharField(required=False, allow_blank=True)
    is_visible = serializers.BooleanField(default=True)

    @staticmethod
    def serialize(t):
        return {
            'id': str(t.id),
            'name': t.name,
            'location': t.location or '',
            'service': t.service or '',
            'quote': t.quote,
            'rating': t.rating,
            'initial': t.initial or (t.name[0].upper() if t.name else 'A'),
            'avatar_bg': t.avatar_bg,
            'is_visible': t.is_visible,
        }

    @classmethod
    def serialize_many(cls, items):
        return [cls.serialize(t) for t in items]


class TestimonialSubmitSerializer(serializers.Serializer):
    """Public-facing: customer can only submit name, location, service, quote, rating."""
    name     = serializers.CharField(max_length=200)
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    service  = serializers.CharField(max_length=100, required=False, allow_blank=True)
    quote    = serializers.CharField(max_length=1000)
    rating   = serializers.IntegerField(min_value=1, max_value=5, default=5)

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Please enter your full name.")
        return value.strip()

    def validate_quote(self, value):
        stripped = value.strip()
        if len(stripped) < 20:
            raise serializers.ValidationError("Please write at least 20 characters.")
        return stripped


# ──────────────────────────────────────────────
# PORTFOLIO
# ──────────────────────────────────────────────
class PortfolioSerializer(serializers.Serializer):
    title      = serializers.CharField(max_length=200)
    category   = serializers.ChoiceField(choices=['bridal', 'editorial', 'glam', 'other'])
    alt_text   = serializers.CharField(max_length=300, required=False, allow_blank=True)
    is_visible = serializers.BooleanField(default=True)
    sort_order = serializers.IntegerField(default=0)

    @staticmethod
    def serialize(p):
        return {
            'id': str(p.id),
            'title': p.title,
            'category': p.category,
            'image_url': p.image_url,
            'alt_text': p.alt_text or '',
            'is_visible': p.is_visible,
            'sort_order': p.sort_order,
        }

    @classmethod
    def serialize_many(cls, items):
        return [cls.serialize(p) for p in items if p.is_visible]


# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


# ──────────────────────────────────────────────
# PAYMENT
# ──────────────────────────────────────────────
class PaymentOrderSerializer(serializers.Serializer):
    amount   = serializers.IntegerField(min_value=100)  # in paise
    currency = serializers.CharField(default='INR', max_length=3)
    booking_id = serializers.CharField(required=False, allow_blank=True)


class PaymentVerifySerializer(serializers.Serializer):
    razorpay_order_id   = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature  = serializers.CharField()
