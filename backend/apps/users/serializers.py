# ============================================
# apps/users/serializers.py
# ============================================

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'phone', 'bio', 'company', 'job_title',
            'website', 'linkedin', 'twitter', 'github', 'avatar',
            'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'phone', 'company', 'job_title'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Password fields didn\'t match.'
            })
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists.')
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Detailed user profile serializer"""
    full_name = serializers.SerializerMethodField()
    events_organized = serializers.SerializerMethodField()
    events_registered = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'phone', 'bio', 'company', 'job_title',
            'website', 'linkedin', 'twitter', 'github', 'avatar',
            'date_joined', 'events_organized', 'events_registered'
        ]
        read_only_fields = ['id', 'username', 'email', 'date_joined']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_events_organized(self, obj):
        return obj.organized_events.count()
    
    def get_events_registered(self, obj):
        return obj.event_registrations.filter(
            status__in=['pending', 'confirmed']
        ).count()
