"""
Glow Guide AI — URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # ── User Auth ─────────────────────────────────────────────────────────
    path('register/',      views.register,      name='glow_register'),
    path('login/',         views.login,          name='glow_login'),
    path('logout/',        views.logout,         name='glow_logout'),
    path('token-refresh/', views.token_refresh,  name='glow_token_refresh'),
    path('profile/',       views.profile,        name='glow_profile'),

    # ── Core Features (🔒 = requires JWT) ────────────────────────────────
    path('chat/',          views.chat,           name='glow_chat'),
    path('chat-history/',  views.chat_history,   name='glow_chat_history'),  # 🔒
    path('skin-analysis/', views.skin_analysis,  name='glow_skin'),           # 🔒
    path('hair-analysis/', views.hair_analysis,  name='glow_hair'),           # 🔒
    path('nail-analysis/', views.nail_analysis,  name='glow_nail'),           # 🔒
    path('daily-tips/',    views.daily_tips,     name='glow_tips'),            # public

    # ── Admin ─────────────────────────────────────────────────────────────
    path('admin/stats/',   views.admin_stats,    name='glow_admin_stats'),
]
