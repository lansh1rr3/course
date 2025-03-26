from django.urls import path
from .views import (
    CustomLoginView, CustomLogoutView, CustomHomeView, CustomSignupView, CustomPasswordResetView,
    CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView,
    UserListView, block_user, unblock_user, ProfileView, ProfileEditView
)

app_name = 'users'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('signup/', CustomSignupView.as_view(), name='signup'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password_reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('', CustomHomeView.as_view(), name='home'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/block/', block_user, name='block_user'),
    path('users/<int:user_id>/unblock/', unblock_user, name='unblock_user'),
    # Новые маршруты
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
]
