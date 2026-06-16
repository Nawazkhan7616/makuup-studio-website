"""
MakuUP Studio — WhatsApp Service via Twilio
Sends booking notification to Noor Khan's WhatsApp.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

SERVICE_LABELS = {
    'bridal':     'Bridal Makeup',
    'editorial':  'Editorial & Fashion',
    'sangeet':    'Sangeet & Event',
    'engagement': 'Engagement Ceremony',
    'mehendi':    'Mehendi Ceremony',
    'everyday':   'Everyday Glam',
    'lessons':    'Makeup Lessons',
    'skincare':   'Pre-Bridal Skincare Prep',
}


def send_whatsapp_notification(booking) -> bool:
    """
    Send a WhatsApp message to Noor Khan when a new booking is received.
    Uses Twilio WhatsApp API (Sandbox or Business API).
    """
    try:
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException
    except ImportError:
        logger.warning("Twilio not installed. WhatsApp notification skipped.")
        return False

    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio credentials not configured. WhatsApp notification skipped.")
        return False

    service_label = SERVICE_LABELS.get(booking.service, booking.service.title())

    message_body = (
        f"💄 *New Booking — MakuUP Studio*\n\n"
        f"*Name:* {booking.name}\n"
        f"*Service:* {service_label}\n"
        f"*Date:* {booking.date}\n"
        f"*Phone:* {booking.phone or 'Not provided'}\n"
        f"*Email:* {booking.email}\n"
    )

    if booking.message:
        message_body += f"*Note:* {booking.message}\n"

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=settings.STUDIO_WHATSAPP_TO,
        )
        logger.info(f"WhatsApp notification sent. SID: {message.sid}")
        return True
    except TwilioRestException as e:
        logger.error(f"Twilio WhatsApp error: {e}")
        return False
    except Exception as e:
        logger.error(f"WhatsApp notification failed: {e}")
        return False
