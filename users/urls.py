# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Importa las nuevas vistas de administración
from .views import (
    RegisterView,
    CurrentUserView, 
    UserAdminListView,
    UserAdminCreateView,
    UserAdminUpdateView,
    UserAdminDeleteView
)


urlpatterns = [
    # URLs públicas
  #  path('user/', CurrentUserView.as_view(), name='current-user'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  #  path('profile/', ProfileView.as_view(), name='profile'),
   path('user/', CurrentUserView.as_view(), name='current-user'),

    # URLs de administración
    path('admin/users/', UserAdminListView.as_view(), name='admin-user-list'),
    path('admin/users/create/', UserAdminCreateView.as_view(), name='admin-user-create'),
    path('admin/users/<int:pk>/update/', UserAdminUpdateView.as_view(), name='admin-user-update'),
    path('admin/users/<int:pk>/delete/', UserAdminDeleteView.as_view(), name='admin-user-delete'),
]