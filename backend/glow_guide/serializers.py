"""
Glow Guide AI — Input Serializers
"""
from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(min_length=1, max_length=1000)
    session_id = serializers.CharField(required=False, allow_blank=True, default='')


class SkinAnalysisSerializer(serializers.Serializer):
    session_id = serializers.CharField(required=False, allow_blank=True, default='')
    age = serializers.CharField(required=False, default='25-34')
    climate = serializers.CharField(required=False, default='tropical')
    skin_type = serializers.CharField(required=True)
    acne = serializers.CharField(required=False, default='none')
    dryness = serializers.CharField(required=False, default='none')
    sensitivity = serializers.CharField(required=False, default='none')
    pigmentation = serializers.CharField(required=False, default='no')
    wrinkles = serializers.CharField(required=False, default='none')
    redness = serializers.CharField(required=False, default='no')
    open_pores = serializers.CharField(required=False, default='no')
    water_intake = serializers.CharField(required=False, default='6-8 glasses')
    sleep_hours = serializers.CharField(required=False, default='7-8')
    stress_level = serializers.CharField(required=False, default='moderate')
    uses_sunscreen = serializers.CharField(required=False, default='sometimes')


class HairAnalysisSerializer(serializers.Serializer):
    session_id = serializers.CharField(required=False, allow_blank=True, default='')
    hair_type = serializers.CharField(required=True)
    scalp_type = serializers.CharField(required=True)
    hair_fall = serializers.CharField(required=False, default='minimal')
    dandruff = serializers.CharField(required=False, default='none')
    frizz = serializers.CharField(required=False, default='none')
    heat_styling = serializers.CharField(required=False, default='rarely')
    wash_frequency = serializers.CharField(required=False, default='2-3 times weekly')
    diet_quality = serializers.CharField(required=False, default='average')
    stress_level = serializers.CharField(required=False, default='moderate')


class NailAnalysisSerializer(serializers.Serializer):
    session_id = serializers.CharField(required=False, allow_blank=True, default='')
    weak_nails = serializers.CharField(required=False, default='no')
    brittle_nails = serializers.CharField(required=False, default='no')
    discoloration = serializers.CharField(required=False, default='no')
    growth_issues = serializers.CharField(required=False, default='no')
    nail_biting = serializers.CharField(required=False, default='no')


class GlowRegisterSerializer(serializers.Serializer):
    name     = serializers.CharField(min_length=2, max_length=100)
    email    = serializers.EmailField()
    password = serializers.CharField(min_length=6, max_length=128, write_only=True)
    session_id = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_name(self, value):
        return value.strip()

    def validate_email(self, value):
        return value.strip().lower()


class GlowLoginSerializer(serializers.Serializer):
    email      = serializers.EmailField()
    password   = serializers.CharField(write_only=True)
    session_id = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_email(self, value):
        return value.strip().lower()


class GlowTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

