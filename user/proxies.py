from .models import CustomUser

class AuthUserProxy(CustomUser):
    class Meta:
        proxy = True
        app_label = 'auth'          # <- shows up under "Authentication and Authorization"
        verbose_name = 'User'
        verbose_name_plural = 'Users'