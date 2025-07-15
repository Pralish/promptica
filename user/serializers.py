from .models import CustomUser
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return value
    
    def validate_username(self, value):
        if CustomUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value
    
    def to_representation(self, instance):
        """Overriding to remove Password Field when returning Data"""
        ret = super().to_representation(instance)
        ret.pop('password', None)
        return ret
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user