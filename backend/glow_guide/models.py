"""
Glow Guide AI — MongoDB Models
"""
from mongoengine import (
    Document, StringField, IntField, ListField, DictField,
    BooleanField, DateTimeField, FloatField, EmailField
)
from datetime import datetime


class GlowUser(Document):
    """Registered user account for Glow Guide AI."""
    email       = EmailField(required=True, unique=True)
    name        = StringField(required=True, max_length=100)
    password    = StringField(required=True)     # bcrypt hash — never plain text
    created_at  = DateTimeField(default=datetime.utcnow)
    last_login  = DateTimeField()

    meta = {
        'collection': 'glow_users',
        'indexes': ['email'],
    }

    def __str__(self):
        return f"{self.name} <{self.email}>"



class GlowSession(Document):
    """Tracks a guest user session across all Glow Guide features."""
    session_id = StringField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.utcnow)
    skin_report_id = StringField(default='')
    hair_report_id = StringField(default='')
    nail_report_id = StringField(default='')

    meta = {'collection': 'glow_sessions'}


class GlowChatHistory(Document):
    """Stores chatbot conversation messages per session."""
    session_id = StringField(required=True)
    user_id    = StringField(default='')   # set after login
    role       = StringField(choices=['user', 'model'], required=True)
    message    = StringField(required=True)
    timestamp  = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'glow_chat_history', 'ordering': ['timestamp'], 'indexes': ['user_id', 'session_id']}


class SkinReport(Document):
    """Stores skin analysis quiz results and AI-generated recommendations."""
    session_id        = StringField(required=True)
    user_id           = StringField(default='')   # set after login
    answers           = DictField()
    skin_type         = StringField(default='')
    health_score      = IntField(default=0)
    hydration_score   = IntField(default=0)
    acne_risk         = StringField(default='low')
    sensitivity_score = IntField(default=0)
    morning_routine   = ListField(DictField())
    night_routine     = ListField(DictField())
    ingredients       = ListField(DictField())
    created_at        = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'skin_reports', 'indexes': ['user_id', 'session_id']}


class HairReport(Document):
    """Stores hair analysis quiz results."""
    session_id             = StringField(required=True)
    user_id                = StringField(default='')   # set after login
    answers                = DictField()
    hair_health_score      = IntField(default=0)
    scalp_health           = StringField(default='')
    hair_type              = StringField(default='')
    growth_recommendations = ListField(StringField())
    weekly_routine         = ListField(DictField())
    ingredients            = ListField(DictField())
    created_at             = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'hair_reports', 'indexes': ['user_id', 'session_id']}


class NailReport(Document):
    """Stores nail analysis quiz results."""
    session_id            = StringField(required=True)
    user_id               = StringField(default='')   # set after login
    answers               = DictField()
    nail_health_score     = IntField(default=0)
    growth_routine        = ListField(StringField())
    hydration_tips        = ListField(StringField())
    color_recommendations = ListField(StringField())
    created_at            = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'nail_reports', 'indexes': ['user_id', 'session_id']}


class DailyTip(Document):
    """Rotating daily wellness tips shown on the blog/tips page."""
    category = StringField(
        choices=['skin', 'hair', 'nail', 'lifestyle', 'nutrition'],
        required=True
    )
    tip = StringField(required=True)
    icon = StringField(default='✨')
    day_number = IntField(default=1)             # 1-30 for rotation
    is_active = BooleanField(default=True)

    meta = {'collection': 'daily_tips'}
