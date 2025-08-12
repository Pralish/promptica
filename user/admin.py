from django.contrib import admin
from rest_framework.authtoken.models import Token

from rest_framework.authtoken.models import TokenProxy
from django.contrib.auth import get_permission_codename
admin.site.unregister(TokenProxy)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from .proxies import AuthUserProxy

# try:
#     admin.site.unregister(CustomUser)
# except admin.sites.NotRegistered:
#     pass

@admin.register(AuthUserProxy)
class AuthUserProxyAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = AuthUserProxy

    list_display = ("email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password", "full_name", "image", "dob", "terms_accepted")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "full_name", "image", "dob",
                       "terms_accepted", "is_staff", "is_active", "groups", "user_permissions"),
        }),
    )
    search_fields = ("email",)
    ordering = ("email",)

    def _has_perm(self, request, action):
        opts = CustomUser._meta
        codename = get_permission_codename(action, opts)
        return request.user.has_perm(f"{opts.app_label}.{codename}")

    def has_view_permission(self, request, obj=None):
        return self._has_perm(request, "view") or self._has_perm(request, "change")

    def has_change_permission(self, request, obj=None):
        return self._has_perm(request, "change")

    def has_add_permission(self, request):
        return self._has_perm(request, "add")

    def has_delete_permission(self, request, obj=None):
        return self._has_perm(request, "delete")
    