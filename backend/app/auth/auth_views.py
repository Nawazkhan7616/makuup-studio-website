"""
MakuUP Studio — Auth views: Login + Logout + Token Refresh
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from app.serializers import LoginSerializer
from app.auth.auth_utils import (
    validate_admin_credentials,
    generate_access_token,
    generate_refresh_token,
    verify_token,
)


@api_view(['POST'])
def login_view(request):
    """
    POST /api/auth/login
    Body: { "username": "noor", "password": "..." }
    Returns: { "access": "...", "refresh": "..." }
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    if not validate_admin_credentials(username, password):
        return Response(
            {'error': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    access_token  = generate_access_token(username)
    refresh_token = generate_refresh_token(username)

    return Response({
        'access':   access_token,
        'refresh':  refresh_token,
        'username': username,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_view(request):
    """
    POST /api/auth/logout
    Client-side: delete the tokens from localStorage.
    Server-side: stateless JWT — just return 200.
    """
    return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def refresh_token_view(request):
    """
    POST /api/auth/refresh
    Body: { "refresh": "<refresh_token>" }
    Returns: { "access": "<new_access_token>" }
    """
    refresh = request.data.get('refresh', '')
    if not refresh:
        return Response({'error': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)

    payload = verify_token(refresh, expected_type='refresh')
    if not payload:
        return Response({'error': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

    new_access = generate_access_token(payload['sub'])
    return Response({'access': new_access}, status=status.HTTP_200_OK)
