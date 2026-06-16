"""
MakuUP Studio — Razorpay Payment Service
Handles order creation and signature verification.
"""
import hmac
import hashlib
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_razorpay_client():
    """Return authenticated Razorpay client."""
    try:
        import razorpay
        return razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    except ImportError:
        raise ImportError("razorpay package not installed.")


def create_order(amount_paise: int, currency: str = 'INR', receipt: str = '') -> dict:
    """
    Create a Razorpay order.
    amount_paise: amount in paise (e.g. ₹500 = 50000 paise)
    Returns: Razorpay order dict or raises exception.
    """
    client = get_razorpay_client()
    order = client.order.create({
        'amount':   amount_paise,
        'currency': currency,
        'receipt':  receipt or f'makuup_{amount_paise}',
        'notes': {
            'studio': 'MakuUP Studio',
            'purpose': 'Booking Advance',
        }
    })
    logger.info(f"Razorpay order created: {order.get('id')}")
    return order


def verify_payment_signature(
    order_id: str,
    payment_id: str,
    signature: str,
) -> bool:
    """
    Verify Razorpay webhook signature.
    Returns True if signature is valid, False otherwise.
    """
    try:
        key_secret = settings.RAZORPAY_KEY_SECRET.encode('utf-8')
        message = f"{order_id}|{payment_id}".encode('utf-8')
        expected = hmac.new(key_secret, message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    except Exception as e:
        logger.error(f"Signature verification failed: {e}")
        return False
