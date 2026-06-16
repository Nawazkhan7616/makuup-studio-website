"""
MakuUP Studio — Custom DRF Permission Classes
"""
from rest_framework.permissions import BasePermission
from app.auth.auth_utils import verify_token


class IsAuthenticatedAdmin(BasePermission):
    """
    Allows access only to requests with a valid JWT access token
    in the Authorization header: "Bearer <token>"
    """
    message = 'Authentication required. Please provide a valid Bearer token.'

    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ', 1)[1].strip()
        payload = verify_token(token, expected_type='access')
        if payload is None:
            return False

        # Attach username to request for downstream use
        request.admin_username = payload.get('sub')
        return True
