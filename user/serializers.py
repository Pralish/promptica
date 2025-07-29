from .models import CustomUser
from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

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
    
class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'password', 'terms_accepted', 'dob']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        user = CustomUser.objects.get(email=self.validated_data['email'])
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"{settings.FRONTEND_BASE_URL}reset-password/?uid={uid}&token={token}"

        send_mail(
            subject="Password Reset",
            message=f"Use this link to reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            self.user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError("Invalid UID")

        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError("Invalid or expired token")
        return attrs

    def save(self):
        self.user.set_password(self.validated_data['password'])
        self.user.save()