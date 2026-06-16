"""
Glow Guide AI — User Authentication Utilities
Handles registration, login, JWT tokens, and guest-to-user session merging.
Uses Python stdlib only for password hashing (no external dependencies).
"""
import jwt
import hashlib
import secrets
import datetime
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# ── Password hashing (stdlib sha256 + random salt) ────────────────────────────
# Format stored: "salt$sha256hex"

def hash_password(plain: str) -> str:
    """Hash a plain-text password using sha256 + random salt."""
    salt = secrets.token_hex(32)
    digest = hashlib.sha256(f"{salt}{plain}".encode()).hexdigest()
    return f"{salt}${digest}"


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against the stored salt$hash."""
    try:
        salt, stored_digest = hashed.split('$', 1)
        candidate = hashlib.sha256(f"{salt}{plain}".encode()).hexdigest()
        return secrets.compare_digest(candidate, stored_digest)
    except Exception:
        return False


# ── JWT token utilities ───────────────────────────────────────────────────────

def _secret() -> str:
    return settings.SECRET_KEY


def generate_user_tokens(user_id: str, email: str) -> dict:
    """
    Issue access + refresh JWT tokens for a Glow Guide user.
    Payload includes user_id and email for easy extraction.
    """
    now = datetime.datetime.utcnow()

    access_payload = {
        'sub':     user_id,
        'email':   email,
        'type':    'gg_access',
        'iat':     now,
        'exp':     now + datetime.timedelta(minutes=getattr(settings, 'JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 60)),
    }
    refresh_payload = {
        'sub':     user_id,
        'email':   email,
        'type':    'gg_refresh',
        'iat':     now,
        'exp':     now + datetime.timedelta(days=getattr(settings, 'JWT_REFRESH_TOKEN_EXPIRE_DAYS', 7)),
    }

    algo = getattr(settings, 'JWT_ALGORITHM', 'HS256')
    return {
        'access':  jwt.encode(access_payload,  _secret(), algorithm=algo),
        'refresh': jwt.encode(refresh_payload, _secret(), algorithm=algo),
    }


def verify_user_token(token: str) -> 'dict | None':
    """
    Verify and decode a Glow Guide user access token.
    Returns payload dict (with 'sub' = user_id, 'email') or None.
    """
    algo = getattr(settings, 'JWT_ALGORITHM', 'HS256')
    try:
        payload = jwt.decode(token, _secret(), algorithms=[algo])
        if payload.get('type') != 'gg_access':
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug('Glow Guide JWT expired.')
        return None
    except jwt.InvalidTokenError as e:
        logger.debug(f'Invalid Glow Guide JWT: {e}')
        return None


def verify_refresh_token(token: str) -> 'dict | None':
    """Verify a Glow Guide user refresh token. Returns payload or None."""
    algo = getattr(settings, 'JWT_ALGORITHM', 'HS256')
    try:
        payload = jwt.decode(token, _secret(), algorithms=[algo])
        if payload.get('type') != 'gg_refresh':
            return None
        return payload
    except jwt.InvalidTokenError:
        return None


def get_user_from_request(request) -> 'dict | None':
    """
    Extract and verify Glow Guide user from Authorization header.
    Returns {'user_id': str, 'email': str} or None if not authenticated.
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:].strip()
    payload = verify_user_token(token)
    if not payload:
        return None
    return {
        'user_id': payload.get('sub'),
        'email':   payload.get('email'),
    }


# ── Guest → User session merge ────────────────────────────────────────────────

def merge_guest_session_to_user(session_id: str, user_id: str) -> dict:
    """
    After a user registers or logs in, attach their user_id to all existing
    guest reports and chat history associated with the session_id.

    Returns a summary dict of how many records were merged.
    """
    from .models import SkinReport, HairReport, NailReport, GlowChatHistory

    counts = {'skin': 0, 'hair': 0, 'nail': 0, 'chat': 0}

    if not session_id or not user_id:
        return counts

    try:
        # Merge skin reports
        skin_q = SkinReport.objects(session_id=session_id, user_id='')
        counts['skin'] = skin_q.count()
        skin_q.update(set__user_id=user_id)

        # Merge hair reports
        hair_q = HairReport.objects(session_id=session_id, user_id='')
        counts['hair'] = hair_q.count()
        hair_q.update(set__user_id=user_id)

        # Merge nail reports
        nail_q = NailReport.objects(session_id=session_id, user_id='')
        counts['nail'] = nail_q.count()
        nail_q.update(set__user_id=user_id)

        # Merge chat history
        chat_q = GlowChatHistory.objects(session_id=session_id, user_id='')
        counts['chat'] = chat_q.count()
        chat_q.update(set__user_id=user_id)

    except Exception as e:
        logger.error(f'Error merging guest session {session_id} to user {user_id}: {e}')

    return counts
