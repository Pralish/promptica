from .models import CustomUser
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'full_name', 'password', 'terms_accepted', 'dob')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return value
        
    def to_representation(self, instance):
        """Overriding to remove Password Field when returning Data"""
        ret = super().to_representation(instance)
        ret.pop('password', None)
        return ret
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user