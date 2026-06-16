"""
Glow Guide AI — API Views
All user-data endpoints are JWT-protected. No cross-user data leakage.
"""
import uuid
from datetime import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import GlowSession, GlowChatHistory, SkinReport, HairReport, NailReport, DailyTip, GlowUser
from .serializers import (
    ChatMessageSerializer, SkinAnalysisSerializer,
    HairAnalysisSerializer, NailAnalysisSerializer,
    GlowRegisterSerializer, GlowLoginSerializer, GlowTokenRefreshSerializer,
)
from .chatbot_engine import get_gemini_response
from .analysis_engine import analyze_skin, analyze_hair, analyze_nail
from .user_auth import (
    hash_password, verify_password,
    generate_user_tokens, verify_refresh_token, get_user_from_request,
    merge_guest_session_to_user,
)


# ─── HELPERS ───────────────────────────────────────────────────────────────

def _require_auth(request):
    """
    Returns (auth_dict, None) if authenticated, or (None, 401 Response) if not.
    Use at the top of any endpoint that requires a logged-in user.
    """
    auth = get_user_from_request(request)
    if not auth:
        return None, Response(
            {'error': 'Authentication required. Please log in to access your data.'},
            status=401
        )
    return auth, None


# ─── USER AUTH ─────────────────────────────────────────────────────────────

@api_view(['POST'])
def register(request):
    """
    POST /api/glow-guide/register/
    Create a new Glow Guide user account.
    Body: { name, email, password, session_id? }
    """
    serializer = GlowRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=400)

    data       = serializer.validated_data
    name       = data['name']
    email      = data['email']
    password   = data['password']
    session_id = data.get('session_id', '')

    if GlowUser.objects(email=email).first():
        return Response({'error': 'An account with this email already exists.'}, status=400)

    try:
        user = GlowUser(
            email    = email,
            name     = name,
            password = hash_password(password),
        ).save()
    except Exception as e:
        return Response({'error': 'Failed to create account. Please try again.'}, status=500)

    user_id = str(user.id)
    tokens  = generate_user_tokens(user_id, email)

    merged = {}
    if session_id:
        merged = merge_guest_session_to_user(session_id, user_id)

    return Response({
        'success': True,
        'user': {'id': user_id, 'name': name, 'email': email},
        'access':  tokens['access'],
        'refresh': tokens['refresh'],
        'merged':  merged,
    }, status=201)


@api_view(['POST'])
def login(request):
    """
    POST /api/glow-guide/login/
    Body: { email, password, session_id? }
    """
    serializer = GlowLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=400)

    data       = serializer.validated_data
    email      = data['email']
    password   = data['password']
    session_id = data.get('session_id', '')

    user = GlowUser.objects(email=email).first()
    if not user or not verify_password(password, user.password):
        return Response({'error': 'Incorrect email or password.'}, status=401)

    try:
        user.last_login = datetime.utcnow()
        user.save()
    except Exception:
        pass

    user_id = str(user.id)
    tokens  = generate_user_tokens(user_id, email)

    merged = {}
    if session_id:
        merged = merge_guest_session_to_user(session_id, user_id)

    return Response({
        'success': True,
        'user': {'id': user_id, 'name': user.name, 'email': email},
        'access':  tokens['access'],
        'refresh': tokens['refresh'],
        'merged':  merged,
    })


@api_view(['POST'])
def logout(request):
    """
    POST /api/glow-guide/logout/
    Stateless JWT — client clears tokens. Backend just confirms.
    """
    return Response({'success': True, 'message': 'Logged out successfully.'})


@api_view(['POST'])
def token_refresh(request):
    """
    POST /api/glow-guide/token-refresh/
    Body: { refresh }
    """
    serializer = GlowTokenRefreshSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': 'Refresh token required.'}, status=400)

    payload = verify_refresh_token(serializer.validated_data['refresh'])
    if not payload:
        return Response({'error': 'Invalid or expired refresh token.'}, status=401)

    tokens = generate_user_tokens(payload['sub'], payload.get('email', ''))
    return Response({'access': tokens['access']})


@api_view(['GET'])
def profile(request):
    """
    GET /api/glow-guide/profile/
    🔒 REQUIRES AUTH — Returns this user's info, reports, and chat history ONLY.
    """
    auth, err = _require_auth(request)
    if err:
        return err

    user_id = auth['user_id']
    user    = GlowUser.objects(id=user_id).first()
    if not user:
        return Response({'error': 'User not found.'}, status=404)

    def serialise_skin(r):
        return {
            'id':              str(r.id),
            'skin_type':       r.skin_type,
            'health_score':    r.health_score,
            'hydration_score': r.hydration_score,
            'acne_risk':       r.acne_risk,
            'morning_routine': r.morning_routine,
            'night_routine':   r.night_routine,
            'ingredients':     r.ingredients,
            'created_at':      r.created_at.isoformat() if r.created_at else '',
        }

    def serialise_hair(r):
        return {
            'id':                    str(r.id),
            'hair_type':             r.hair_type,
            'scalp_health':          r.scalp_health,
            'hair_health_score':     r.hair_health_score,
            'growth_recommendations': r.growth_recommendations,
            'weekly_routine':        r.weekly_routine,
            'ingredients':           r.ingredients,
            'created_at':            r.created_at.isoformat() if r.created_at else '',
        }

    def serialise_nail(r):
        return {
            'id':                  str(r.id),
            'nail_health_score':   r.nail_health_score,
            'growth_routine':      r.growth_routine,
            'hydration_tips':      r.hydration_tips,
            'color_recommendations': r.color_recommendations,
            'created_at':          r.created_at.isoformat() if r.created_at else '',
        }

    try:
        # ── All queries strictly filtered by this user's ID ──
        skin_reports = [serialise_skin(r) for r in SkinReport.objects(user_id=user_id).order_by('-created_at').limit(5)]
        hair_reports = [serialise_hair(r) for r in HairReport.objects(user_id=user_id).order_by('-created_at').limit(5)]
        nail_reports = [serialise_nail(r) for r in NailReport.objects(user_id=user_id).order_by('-created_at').limit(5)]
        chat_history = [
            {'role': h.role, 'message': h.message, 'time': h.timestamp.isoformat() if h.timestamp else ''}
            for h in GlowChatHistory.objects(user_id=user_id).order_by('-timestamp').limit(40)
        ]
    except Exception as e:
        return Response({'error': f'Failed to load profile data: {str(e)}'}, status=500)

    return Response({
        'success': True,
        'user': {
            'id':           user_id,
            'name':         user.name,
            'email':        user.email,
            'member_since': user.created_at.isoformat() if user.created_at else '',
            'last_login':   user.last_login.isoformat() if user.last_login else '',
        },
        'skin_reports': skin_reports,
        'hair_reports': hair_reports,
        'nail_reports': nail_reports,
        'chat_history': list(reversed(chat_history)),  # oldest first
    })


# ─── CHATBOT ───────────────────────────────────────────────────────────────

@api_view(['POST'])
def chat(request):
    """
    POST /api/glow-guide/chat/
    🔒 Authenticated users → private history loaded/saved by user_id only.
    👤 Guest users → history loaded/saved by session_id only (isolated per session).

    SECURITY: A user can NEVER see another user's messages.
    """
    serializer = ChatMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=400)

    message    = serializer.validated_data['message']
    session_id = serializer.validated_data.get('session_id', '').strip()

    # Resolve identity: prefer JWT user_id over session_id
    auth    = get_user_from_request(request)
    user_id = auth['user_id'] if auth else ''

    # ── Load conversation history — strictly by owner ──────────────────────
    history = []
    try:
        if user_id:
            # Authenticated: load ONLY this user's messages
            history_qs = GlowChatHistory.objects(user_id=user_id).order_by('timestamp')[:40]
        elif session_id:
            # Guest: load ONLY this anonymous session's messages
            history_qs = GlowChatHistory.objects(
                session_id=session_id,
                user_id=''   # explicitly exclude any user-owned records
            ).order_by('timestamp')[:40]
        else:
            history_qs = []
        history = [{'role': h.role, 'message': h.message} for h in history_qs]
    except Exception:
        history = []

    # ── Load user context for personalisation (this user only) ─────────────
    user_context = {}
    if user_id:
        try:
            skin = SkinReport.objects(user_id=user_id).order_by('-created_at').first()
            if skin:
                user_context['skin_type'] = skin.skin_type
                user_context['acne_risk'] = skin.acne_risk
        except Exception:
            pass
        try:
            hair = HairReport.objects(user_id=user_id).order_by('-created_at').first()
            if hair:
                user_context['hair_type']    = hair.hair_type
                user_context['scalp_health'] = hair.scalp_health
        except Exception:
            pass
    elif session_id:
        try:
            skin = SkinReport.objects(session_id=session_id, user_id='').order_by('-created_at').first()
            if skin:
                user_context['skin_type'] = skin.skin_type
                user_context['acne_risk'] = skin.acne_risk
        except Exception:
            pass

    # ── Get AI response ────────────────────────────────────────────────────
    ai_response, error = get_gemini_response(message, history, user_context)

    if not ai_response:
        return Response({'error': 'AI service temporarily unavailable.'}, status=503)

    # ── Persist — tagged with owner (user_id OR session_id, never both empty) ──
    if user_id or session_id:
        try:
            GlowChatHistory(
                session_id = session_id or f'user_{user_id}',
                user_id    = user_id,
                role       = 'user',
                message    = message,
            ).save()
            GlowChatHistory(
                session_id = session_id or f'user_{user_id}',
                user_id    = user_id,
                role       = 'model',
                message    = ai_response,
            ).save()
        except Exception:
            pass

    return Response({'success': True, 'response': ai_response, 'session_id': session_id})


@api_view(['GET'])
def chat_history(request):
    """
    GET /api/glow-guide/chat-history/
    🔒 REQUIRES AUTH — Returns ONLY the current user's chat history.
    Used by the frontend to restore messages after login.
    """
    auth, err = _require_auth(request)
    if err:
        return err

    user_id = auth['user_id']
    try:
        messages = [
            {
                'role':    h.role,
                'message': h.message,
                'time':    h.timestamp.isoformat() if h.timestamp else '',
            }
            for h in GlowChatHistory.objects(user_id=user_id).order_by('timestamp').limit(60)
        ]
        return Response({'success': True, 'history': messages})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# ─── SKIN ANALYSIS ─────────────────────────────────────────────────────────

@api_view(['POST'])
def skin_analysis(request):
    """
    POST /api/glow-guide/skin-analysis/
    🔒 REQUIRES AUTH — Report is saved and retrievable only by this user.
    """
    auth, err = _require_auth(request)
    if err:
        return err

    serializer = SkinAnalysisSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=400)

    answers    = serializer.validated_data
    session_id = answers.pop('session_id', '') or str(uuid.uuid4())
    user_id    = auth['user_id']

    result = analyze_skin(answers)

    try:
        SkinReport(
            session_id        = session_id,
            user_id           = user_id,          # always tied to this user
            answers           = answers,
            skin_type         = result['skin_type'],
            health_score      = result['health_score'],
            hydration_score   = result['hydration_score'],
            acne_risk         = result['acne_risk'],
            sensitivity_score = result['sensitivity_score'],
            morning_routine   = result['morning_routine'],
            night_routine     = result['night_routine'],
            ingredients       = result['ingredients'],
        ).save()
    except Exception:
        pass

    return Response({'success': True, 'session_id': session_id, 'report': result})


# ─── HAIR ANALYSIS ─────────────────────────────────────────────────────────

@api_view(['POST'])
def hair_analysis(request):
    """
    POST /api/glow-guide/hair-analysis/
    🔒 REQUIRES AUTH — Report saved under this user only.
    """
    auth, err = _require_auth(request)
    if err:
        return err

    serializer = HairAnalysisSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=400)

    answers    = serializer.validated_data
    session_id = answers.pop('session_id', '') or str(uuid.uuid4())
    user_id    = auth['user_id']

    result = analyze_hair(answers)

    try:
        HairReport(
            session_id             = session_id,
            user_id                = user_id,
            answers                = answers,
            hair_health_score      = result['hair_health_score'],
            scalp_health           = result['scalp_health'],
            hair_type              = result['hair_type'],
            growth_recommendations = result['growth_recommendations'],
            weekly_routine         = result['weekly_routine'],
            ingredients            = result['ingredients'],
        ).save()
    except Exception:
        pass

    return Response({'success': True, 'session_id': session_id, 'report': result})


# ─── NAIL ANALYSIS ─────────────────────────────────────────────────────────

@api_view(['POST'])
def nail_analysis(request):
    """
    POST /api/glow-guide/nail-analysis/
    🔒 REQUIRES AUTH — Report saved under this user only.
    """
    auth, err = _require_auth(request)
    if err:
        return err

    serializer = NailAnalysisSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=400)

    answers    = serializer.validated_data
    session_id = answers.pop('session_id', '') or str(uuid.uuid4())
    user_id    = auth['user_id']

    result = analyze_nail(answers)

    try:
        NailReport(
            session_id            = session_id,
            user_id               = user_id,
            answers               = answers,
            nail_health_score     = result['nail_health_score'],
            growth_routine        = result['growth_routine'],
            hydration_tips        = result['hydration_tips'],
            color_recommendations = result['color_recommendations'],
        ).save()
    except Exception:
        pass

    return Response({'success': True, 'session_id': session_id, 'report': result})


# ─── DAILY TIPS (public — no user data) ───────────────────────────────────

DEFAULT_TIPS = [
    {'category': 'skin',      'tip': 'Reapply sunscreen every 2-3 hours when outdoors.', 'icon': '☀️', 'day_number': 1},
    {'category': 'lifestyle', 'tip': 'Drink at least 8 glasses of water today for glowing skin.', 'icon': '💧', 'day_number': 2},
    {'category': 'hair',      'tip': 'Massage your scalp for 5 minutes today to boost circulation.', 'icon': '💆', 'day_number': 3},
    {'category': 'nail',      'tip': 'Apply cuticle oil before sleeping tonight for stronger nails.', 'icon': '✨', 'day_number': 4},
    {'category': 'skin',      'tip': 'Sleep before 11 PM — your skin repairs itself between 10PM-2AM.', 'icon': '🌙', 'day_number': 5},
    {'category': 'nutrition', 'tip': 'Eat 1 tablespoon of flaxseeds today for Omega-3 and glowing skin.', 'icon': '🌱', 'day_number': 6},
    {'category': 'skin',      'tip': 'Remove all makeup before sleeping — never skip this step.', 'icon': '🧴', 'day_number': 7},
    {'category': 'lifestyle', 'tip': 'Do 10 minutes of deep breathing to reduce cortisol — stress ages skin.', 'icon': '🧘', 'day_number': 8},
    {'category': 'hair',      'tip': 'Air-dry your hair today instead of blow-drying for healthier strands.', 'icon': '💨', 'day_number': 9},
    {'category': 'skin',      'tip': 'Apply lip balm and let your lips be bare today — they need rest too.', 'icon': '💋', 'day_number': 10},
    {'category': 'nutrition', 'tip': 'Have amla (Indian gooseberry) today — it has 20x more Vitamin C than oranges.', 'icon': '🍃', 'day_number': 11},
    {'category': 'skin',      'tip': 'Use a clean towel or tissue to pat your face dry. Never rub!', 'icon': '🤍', 'day_number': 12},
    {'category': 'nail',      'tip': 'File your nails in one direction only to prevent splitting.', 'icon': '💅', 'day_number': 13},
    {'category': 'lifestyle', 'tip': 'Change your pillowcase today — it collects bacteria that cause breakouts.', 'icon': '🛏️', 'day_number': 14},
    {'category': 'skin',      'tip': 'Wash your face brushes and beauty tools this week.', 'icon': '🪥', 'day_number': 15},
    {'category': 'hair',      'tip': 'Do a cold water rinse after conditioning to seal hair cuticles.', 'icon': '❄️', 'day_number': 16},
    {'category': 'nutrition', 'tip': 'Add turmeric to your food or milk today — it is a powerful anti-inflammatory.', 'icon': '🌿', 'day_number': 17},
    {'category': 'skin',      'tip': 'Apply sunscreen on your neck and hands too — they age fastest.', 'icon': '🌟', 'day_number': 18},
    {'category': 'lifestyle', 'tip': 'Step away from screens for 30 minutes today — blue light affects skin health.', 'icon': '📴', 'day_number': 19},
    {'category': 'nail',      'tip': 'Wear gloves while doing dishes to protect your nails from harsh detergents.', 'icon': '🧤', 'day_number': 20},
    {'category': 'hair',      'tip': 'Use a wide-tooth comb on wet hair to reduce breakage.', 'icon': '♾️', 'day_number': 21},
    {'category': 'skin',      'tip': 'Do a gentle 60-second facial massage during your nighttime routine.', 'icon': '✋', 'day_number': 22},
    {'category': 'nutrition', 'tip': 'Include walnuts in your diet today — they are the best nut for hair and skin.', 'icon': '🌰', 'day_number': 23},
    {'category': 'lifestyle', 'tip': 'Clean your phone screen — it transfers bacteria to your face constantly.', 'icon': '📱', 'day_number': 24},
    {'category': 'skin',      'tip': 'Use a clean face towel — towels harbour bacteria after 2-3 uses.', 'icon': '🧼', 'day_number': 25},
    {'category': 'hair',      'tip': 'Avoid tight ponytails today — they cause hair breakage at the hairline.', 'icon': '👧', 'day_number': 26},
    {'category': 'nutrition', 'tip': 'Have a handful of pumpkin seeds — they are high in zinc, great for skin and hair.', 'icon': '🎃', 'day_number': 27},
    {'category': 'skin',      'tip': 'Try a DIY face mask: mix 1 tsp honey + 1 tsp turmeric for a glow boost.', 'icon': '🍯', 'day_number': 28},
    {'category': 'nail',      'tip': 'Give your nails a break from nail polish for 2-3 days this week.', 'icon': '🕊️', 'day_number': 29},
    {'category': 'lifestyle', 'tip': 'Start your day with a glass of warm lemon water for skin detox.', 'icon': '🍋', 'day_number': 30},
]


@api_view(['GET'])
def daily_tips(request):
    """Public — no user data involved."""
    from datetime import date
    day_of_year  = date.today().timetuple().tm_yday
    today_index  = (day_of_year - 1) % len(DEFAULT_TIPS)
    today_tip    = DEFAULT_TIPS[today_index]
    extras       = [DEFAULT_TIPS[(today_index + i) % len(DEFAULT_TIPS)] for i in range(1, 4)]
    return Response({'success': True, 'today': today_tip, 'more_tips': extras})


# ─── ADMIN STATS ───────────────────────────────────────────────────────────

@api_view(['GET'])
def admin_stats(request):
    """Admin-only: aggregate stats only — no individual user data."""
    from app.permissions import IsAuthenticatedAdmin
    perm = IsAuthenticatedAdmin()
    if not perm.has_permission(request, None):
        return Response({'error': 'Unauthorized'}, status=401)

    try:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return Response({
            'success': True,
            'stats': {
                'total_users':         GlowUser.objects.count(),
                'total_chat_messages': GlowChatHistory.objects(role='user').count(),
                'total_skin_analyses': SkinReport.objects.count(),
                'total_hair_analyses': HairReport.objects.count(),
                'total_nail_analyses': NailReport.objects.count(),
                'today_chats':         GlowChatHistory.objects(role='user', timestamp__gte=today_start).count(),
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)
