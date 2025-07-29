from django.urls import path
from .views import SignUpView, SignInView, CurrentUserView, SendPasswordResetEmail, PasswordResetConfirm, UpdateUserView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('current-user/', CurrentUserView.as_view(), name='current-user'),
    path('password-reset/', SendPasswordResetEmail.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('update/', UpdateUserView.as_view(), name='update-user'),

]
