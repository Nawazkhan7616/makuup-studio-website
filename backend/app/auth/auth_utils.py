"""
MakuUP Studio — JWT Auth Utilities
Single-user auth: credentials stored in .env, no DB needed.
Uses PyJWT to issue/verify access + refresh tokens.
"""
import jwt
import datetime
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

ACCESS_TOKEN_TYPE  = 'access'
REFRESH_TOKEN_TYPE = 'refresh'


def _secret() -> str:
    return settings.SECRET_KEY


def generate_access_token(username: str) -> str:
    """Issue a short-lived access token (default 60 min)."""
    payload = {
        'sub':  username,
        'type': ACCESS_TOKEN_TYPE,
        'iat':  datetime.datetime.utcnow(),
        'exp':  datetime.datetime.utcnow() + datetime.timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }
    return jwt.encode(payload, _secret(), algorithm=settings.JWT_ALGORITHM)


def generate_refresh_token(username: str) -> str:
    """Issue a long-lived refresh token (default 7 days)."""
    payload = {
        'sub':  username,
        'type': REFRESH_TOKEN_TYPE,
        'iat':  datetime.datetime.utcnow(),
        'exp':  datetime.datetime.utcnow() + datetime.timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        ),
    }
    return jwt.encode(payload, _secret(), algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str, expected_type: str = ACCESS_TOKEN_TYPE) -> 'dict | None':
    """
    Verify and decode a JWT token.
    Returns payload dict on success, None on failure.
    """
    try:
        payload = jwt.decode(token, _secret(), algorithms=[settings.JWT_ALGORITHM])
        if payload.get('type') != expected_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("JWT expired.")
        return None
    except jwt.InvalidTokenError as e:
        logger.debug(f"Invalid JWT: {e}")
        return None


def validate_admin_credentials(username: str, password: str) -> bool:
    """Check username+password against .env config (constant-time comparison)."""
    import hmac
    expected_user = settings.ADMIN_USERNAME.encode()
    expected_pass = settings.ADMIN_PASSWORD.encode()
    user_match = hmac.compare_digest(username.encode(), expected_user)
    pass_match = hmac.compare_digest(password.encode(), expected_pass)
    return user_match and pass_match
