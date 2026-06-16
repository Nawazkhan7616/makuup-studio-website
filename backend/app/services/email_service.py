"""
MakuUP Studio -- Email Service
Sends booking confirmation to client + notification to Noor Khan.
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings


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


def _service_label(slug: str) -> str:
    return SERVICE_LABELS.get(slug, slug.title())


def send_booking_confirmation(booking) -> bool:
    """Send confirmation email to the client who booked."""
    service_label = _service_label(booking.service)
    subject = f"Booking Confirmation - {settings.STUDIO_NAME}"

    # ASCII-safe plain text (no Unicode box-drawing or emoji)
    text_body = (
        f"Hello {booking.name},\n\n"
        f"Thank you for booking with {settings.STUDIO_NAME}!\n\n"
        f"Your appointment details:\n"
        f"--------------------\n"
        f"Service : {service_label}\n"
        f"Date    : {booking.date}\n"
        f"--------------------\n\n"
        f"We will contact you shortly to confirm your appointment.\n\n"
        f"If you have any questions, simply reply to this email or WhatsApp us.\n\n"
        f"With love & glam,\n"
        f"Noor Khan\n"
        f"{settings.STUDIO_NAME}\n"
        f"hello@makuupstudio.in\n"
    )

    html_body = (
        "<html>"
        "<body style=\"font-family: Arial, sans-serif; background:#0d0d0d; color:#f5f0eb; padding:40px 0;\">"
        "<table width=\"600\" align=\"center\" style=\"background:#1a1a1a; border-radius:12px; overflow:hidden; padding:0;\">"
        "<tr>"
        "<td style=\"background:linear-gradient(135deg,#e96cba,#a855f7); padding:32px 40px; text-align:center;\">"
        "<h1 style=\"margin:0; font-size:28px; color:#fff; letter-spacing:2px;\">"
        f"MakuUP <span style=\"font-size:14px; letter-spacing:4px;\">STUDIO</span>"
        "</h1>"
        "</td>"
        "</tr>"
        "<tr>"
        "<td style=\"padding:40px;\">"
        "<h2 style=\"color:#e96cba; margin:0 0 16px;\">Booking Confirmed!</h2>"
        f"<p style=\"color:#c8bfb5; line-height:1.7;\">Hello <strong style=\"color:#f5f0eb;\">{booking.name}</strong>,</p>"
        f"<p style=\"color:#c8bfb5; line-height:1.7;\">Thank you for booking with <strong style=\"color:#e96cba;\">{settings.STUDIO_NAME}</strong>! Here are your appointment details:</p>"
        "<table width=\"100%\" style=\"background:#111; border-radius:8px; padding:24px; margin:24px 0;\">"
        "<tr>"
        "<td style=\"color:#a0978e; padding:8px 0; font-size:14px;\">SERVICE</td>"
        f"<td style=\"color:#f5f0eb; padding:8px 0; font-weight:600;\">{service_label}</td>"
        "</tr>"
        "<tr>"
        "<td style=\"color:#a0978e; padding:8px 0; font-size:14px;\">DATE</td>"
        f"<td style=\"color:#f5f0eb; padding:8px 0; font-weight:600;\">{booking.date}</td>"
        "</tr>"
        "</table>"
        "<p style=\"color:#c8bfb5; line-height:1.7;\">We will contact you shortly to confirm your exact time slot.</p>"
        "<p style=\"color:#c8bfb5; line-height:1.7;\">Questions? Just reply to this email.</p>"
        "<div style=\"margin-top:40px; padding-top:24px; border-top:1px solid #2a2a2a; text-align:center; color:#a0978e; font-size:13px;\">"
        "With love & glam,<br/>"
        f"<strong style=\"color:#e96cba;\">Noor Khan -- {settings.STUDIO_NAME}</strong>"
        "</div>"
        "</td>"
        "</tr>"
        "</table>"
        "</body>"
        "</html>"
    )

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.STUDIO_EMAIL,
            to=[booking.email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.encoding = 'utf-8'
        msg.send()
        return True
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Confirmation email skipped: {e}")
        return False


def send_booking_notification(booking) -> bool:
    """Send new booking notification to Noor Khan."""
    service_label = _service_label(booking.service)
    subject = f"New Booking: {booking.name} - {service_label}"

    body = (
        f"New booking received on MakuUP Studio website!\n\n"
        f"--------------------\n"
        f"Name    : {booking.name}\n"
        f"Email   : {booking.email}\n"
        f"Phone   : {booking.phone or 'Not provided'}\n"
        f"Service : {service_label}\n"
        f"Date    : {booking.date}\n"
        f"Message : {booking.message or '-'}\n"
        f"--------------------\n\n"
        f"Log in to your dashboard to update the booking status.\n"
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.STUDIO_EMAIL,
            recipient_list=[settings.STUDIO_OWNER_EMAIL],
            fail_silently=True,   # Never block the booking if email fails
        )
        return True
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Notification email skipped: {e}")
        return False
