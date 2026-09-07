from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    GoogleAuthView,
    SetRoleView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    DeleteAccountView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('google/', GoogleAuthView.as_view(), name='auth-google'),
    path('google/role/', SetRoleView.as_view(), name='auth-google-role'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('delete/', DeleteAccountView.as_view(), name='auth-delete'),
]
