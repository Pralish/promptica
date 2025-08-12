from django.contrib import admin
from rest_framework.authtoken.models import Token

from rest_framework.authtoken.models import TokenProxy
admin.site.unregister(TokenProxy)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from .proxies import AuthUserProxy

try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

@admin.register(AuthUserProxy)
class AuthUserProxyAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = AuthUserProxy
    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)