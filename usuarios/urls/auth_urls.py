from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from ..views import LoginView, LogoutView, RequestPasswordResetView, ConfirmPasswordResetView

urlpatterns = [
    path('auth/login/',  LoginView.as_view(),  name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/password-reset/', RequestPasswordResetView.as_view(), name='password_reset'),
    path('auth/password-reset-confirm/', ConfirmPasswordResetView.as_view(), name='password_reset_confirm'),
]