"""
MakuUP Studio — Main API Views
All endpoints for bookings, portfolio, testimonials, and payments.
"""
import logging
import threading
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from app.models import Booking, Testimonial, PortfolioImage
from app.serializers import (
    BookingCreateSerializer,
    BookingStatusSerializer,
    BookingListSerializer,
    TestimonialSerializer,
    TestimonialSubmitSerializer,
    PortfolioSerializer,
    PaymentOrderSerializer,
    PaymentVerifySerializer,
)
from app.permissions import IsAuthenticatedAdmin
from app.services import email_service, whatsapp_service, payment_service

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """GET /api/health/ — simple liveness probe."""
    return Response({'status': 'ok', 'studio': 'MakuUP Studio API'})


# ═══════════════════════════════════════════════════
# BOOKINGS — PUBLIC
# ═══════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    """
    POST /api/bookings/create
    Public endpoint. Validates, saves booking, sends emails + WhatsApp.
    """
    serializer = BookingCreateSerializer(data=request.data)
    if not serializer.is_valid():
        # Build a human-readable message from DRF errors
        first_error = next(iter(serializer.errors.values()))
        first_msg = first_error[0] if isinstance(first_error, list) else str(first_error)
        return Response(
            {'error': str(first_msg), 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = serializer.validated_data
    booking_date = data['date']  # already a string "YYYY-MM-DD"

    # ── Overbooking check ────────────────────────────────────────────────
    max_per_day = settings.MAX_BOOKINGS_PER_DATE
    try:
        existing_count = Booking.objects.filter(date=booking_date).count()
        if existing_count >= max_per_day:
            return Response(
                {
                    'error': 'overbooking',
                    'message': (
                        f"Sorry, we are fully booked on {booking_date}. "
                        "Please choose a different date."
                    ),
                },
                status=status.HTTP_409_CONFLICT,
            )
    except Exception as e:
        logger.warning(f"Overbooking check failed (DB issue): {e}")
        # Don't block the booking if we can't check — proceed to save

    # ── Save to MongoDB ──────────────────────────────────────────────────
    try:
        booking = Booking(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            service=data['service'],
            date=booking_date,
            message=data.get('message', ''),
            status='new',
        )
        booking.save()
    except Exception as e:
        logger.error(f"Failed to save booking: {e}")
        return Response(
            {'error': 'Could not save your booking. Please try again in a moment.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # ── Send notifications in background thread (non-blocking) ──────────
    def send_notifications():
        try:
            email_service.send_booking_confirmation(booking)
            email_service.send_booking_notification(booking)
            whatsapp_service.send_whatsapp_notification(booking)
        except Exception as e:
            logger.error(f"Notification error: {e}")

    thread = threading.Thread(target=send_notifications, daemon=True)
    thread.start()

    return Response(
        {
            'success': True,
            'message': "Booking received! We'll contact you within 24 hours.",
            'booking_id': str(booking.id),
        },
        status=status.HTTP_201_CREATED,
    )


# ═══════════════════════════════════════════════════
# BOOKINGS — PROTECTED (Dashboard)
# ═══════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticatedAdmin])
def list_bookings(request):
    """
    GET /api/bookings/list
    Protected. Supports ?search=, ?status=, ?date= query params.
    """
    bookings = Booking.objects.all()

    # Filters
    search = request.query_params.get('search', '').strip()
    filter_status = request.query_params.get('status', '').strip()
    filter_date = request.query_params.get('date', '').strip()

    if search:
        # MongoEngine icontains filter
        from mongoengine.queryset.visitor import Q
        bookings = bookings.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    if filter_status and filter_status in ('new', 'contacted', 'confirmed'):
        bookings = bookings.filter(status=filter_status)

    if filter_date:
        bookings = bookings.filter(date=filter_date)

    data = BookingListSerializer.serialize_many(bookings)
    return Response({'bookings': data, 'count': len(data)})


@api_view(['DELETE'])
@permission_classes([IsAuthenticatedAdmin])
def delete_booking(request, booking_id):
    """
    DELETE /api/bookings/delete/<booking_id>
    Protected.
    """
    try:
        booking = Booking.objects.get(id=booking_id)
    except (Booking.DoesNotExist, Exception):
        return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

    booking.delete()
    return Response({'success': True, 'message': 'Booking deleted.'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticatedAdmin])
def update_booking_status(request, booking_id):
    """
    PATCH /api/bookings/update-status/<booking_id>
    Body: { "status": "contacted" | "confirmed" | "new" }
    Protected.
    """
    try:
        booking = Booking.objects.get(id=booking_id)
    except (Booking.DoesNotExist, Exception):
        return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = BookingStatusSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid status.', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    booking.status = serializer.validated_data['status']
    booking.save()

    return Response({
        'success': True,
        'booking_id': str(booking.id),
        'status': booking.status,
    })


# ═══════════════════════════════════════════════════
# PORTFOLIO
# ═══════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def list_portfolio(request):
    """GET /api/portfolio/ — returns all visible portfolio images."""
    images = PortfolioImage.objects.filter(is_visible=True)
    data = PortfolioSerializer.serialize_many(images)
    return Response({'portfolio': data, 'count': len(data)})


@api_view(['POST'])
@permission_classes([IsAuthenticatedAdmin])
def upload_portfolio(request):
    """
    POST /api/portfolio/upload
    Protected. Expects multipart/form-data with 'image' file field + metadata.
    Uploads to Cloudinary and saves URL in MongoDB.
    """
    serializer = PortfolioSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Validation failed.', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    image_file = request.FILES.get('image')
    if not image_file:
        return Response({'error': 'No image file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    # Upload to Cloudinary
    try:
        import cloudinary.uploader
        import cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
        )
        result = cloudinary.uploader.upload(
            image_file,
            folder='makuup_studio/portfolio',
            resource_type='image',
        )
        image_url = result.get('secure_url', '')
        public_id = result.get('public_id', '')
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        return Response(
            {'error': 'Image upload failed. Check Cloudinary credentials.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    data = serializer.validated_data
    portfolio_item = PortfolioImage(
        title=data['title'],
        category=data['category'],
        image_url=image_url,
        public_id=public_id,
        alt_text=data.get('alt_text', ''),
        is_visible=data.get('is_visible', True),
        sort_order=data.get('sort_order', 0),
    )
    portfolio_item.save()

    return Response({
        'success': True,
        'id': str(portfolio_item.id),
        'image_url': image_url,
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticatedAdmin])
def delete_portfolio_item(request, item_id):
    """DELETE /api/portfolio/delete/<item_id> — Protected."""
    try:
        item = PortfolioImage.objects.get(id=item_id)
    except Exception:
        return Response({'error': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Delete from Cloudinary if public_id is set
    if item.public_id:
        try:
            import cloudinary.uploader
            cloudinary.uploader.destroy(item.public_id)
        except Exception as e:
            logger.warning(f"Cloudinary deletion failed: {e}")

    item.delete()
    return Response({'success': True, 'message': 'Portfolio item deleted.'})


# ═══════════════════════════════════════════════════
# TESTIMONIALS
# ═══════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def list_testimonials(request):
    """GET /api/testimonials/ — returns all visible testimonials."""
    testimonials = Testimonial.objects.filter(is_visible=True)
    data = TestimonialSerializer.serialize_many(testimonials)
    return Response({'testimonials': data, 'count': len(data)})


@api_view(['POST'])
@permission_classes([IsAuthenticatedAdmin])
def create_testimonial(request):
    """POST /api/testimonials/create — Protected."""
    serializer = TestimonialSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Validation failed.', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    data = serializer.validated_data
    testi = Testimonial(**data)
    testi.save()
    return Response(
        {'success': True, 'id': str(testi.id)},
        status=status.HTTP_201_CREATED,
    )


@api_view(['PATCH'])
@permission_classes([IsAuthenticatedAdmin])
def update_testimonial(request, testi_id):
    """PATCH /api/testimonials/update/<testi_id> — Protected."""
    try:
        testi = Testimonial.objects.get(id=testi_id)
    except Exception:
        return Response({'error': 'Testimonial not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TestimonialSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
            {'error': 'Validation failed.', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    for field, value in serializer.validated_data.items():
        setattr(testi, field, value)
    testi.save()

    return Response({'success': True, 'id': str(testi.id)})


@api_view(['DELETE'])
@permission_classes([IsAuthenticatedAdmin])
def delete_testimonial(request, testi_id):
    """DELETE /api/testimonials/delete/<testi_id> — Protected."""
    try:
        testi = Testimonial.objects.get(id=testi_id)
    except Exception:
        return Response({'error': 'Testimonial not found.'}, status=status.HTTP_404_NOT_FOUND)

    testi.delete()
    return Response({'success': True, 'message': 'Testimonial deleted.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_testimonial(request):
    """
    POST /api/testimonials/submit/ — Public.
    Customer submission stored with is_visible=False (pending moderation).
    """
    serializer = TestimonialSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Validation failed.', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    data = serializer.validated_data
    testi = Testimonial(
        name=data['name'],
        location=data.get('location', ''),
        service=data.get('service', ''),
        quote=data['quote'],
        rating=data.get('rating', 5),
        is_visible=False,   # ← awaiting admin approval
    )
    testi.save()
    return Response(
        {'success': True, 'message': 'Thank you! Your review is under review and will appear soon.'},
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticatedAdmin])
def list_pending_testimonials(request):
    """GET /api/testimonials/pending/ — Protected. Returns pending testimonials."""
    pending = Testimonial.objects.filter(is_visible=False)
    data = TestimonialSerializer.serialize_many(pending)
    return Response({'testimonials': data, 'count': len(data)})


@api_view(['PATCH'])
@permission_classes([IsAuthenticatedAdmin])
def approve_testimonial(request, testi_id):
    """PATCH /api/testimonials/approve/<testi_id>/ — Protected. Approves a pending review."""
    try:
        testi = Testimonial.objects.get(id=testi_id)
    except Exception:
        return Response({'error': 'Testimonial not found.'}, status=status.HTTP_404_NOT_FOUND)
    testi.is_visible = True
    testi.save()
    return Response({'success': True, 'id': str(testi.id)})



# ═══════════════════════════════════════════════════
# PAYMENTS — Razorpay
# ═══════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def create_payment_order(request):
    """
    POST /api/payment/create-order
    Body: { "amount": 50000, "currency": "INR", "booking_id": "..." }
    amount is in paise (₹500 = 50000 paise)
    """
    serializer = PaymentOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Validation failed.', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = serializer.validated_data
    try:
        order = payment_service.create_order(
            amount_paise=data['amount'],
            currency=data.get('currency', 'INR'),
            receipt=data.get('booking_id', ''),
        )
        return Response({
            'order_id':  order['id'],
            'amount':    order['amount'],
            'currency':  order['currency'],
            'key_id':    settings.RAZORPAY_KEY_ID,
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {e}")
        return Response(
            {'error': 'Payment order creation failed.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_payment(request):
    """
    POST /api/payment/verify
    Body: { razorpay_order_id, razorpay_payment_id, razorpay_signature }
    """
    serializer = PaymentVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Missing payment verification fields.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = serializer.validated_data
    is_valid = payment_service.verify_payment_signature(
        order_id=data['razorpay_order_id'],
        payment_id=data['razorpay_payment_id'],
        signature=data['razorpay_signature'],
    )

    if is_valid:
        return Response({'success': True, 'message': 'Payment verified.'})
    else:
        return Response(
            {'error': 'Payment signature verification failed.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
