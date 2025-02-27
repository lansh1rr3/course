# clients/urls.py
from django.urls import path
from . import views, auth_views

urlpatterns = [
    # Клиенты
    path('', views.ClientListView.as_view(), name='client_list'),
    path('create/', views.client_create, name='client_create'),
    path('<int:pk>/update/', views.client_update, name='client_update'),
    path('<int:pk>/delete/', views.client_delete, name='client_delete'),
    # Сообщения
    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/create/', views.message_create, name='message_create'),
    path('messages/<int:pk>/update/', views.message_update, name='message_update'),
    path('messages/<int:pk>/delete/', views.message_delete, name='message_delete'),
    # Рассылки
    path('mailings/', views.MailingListView.as_view(), name='mailing_list'),
    path('mailings/create/', views.mailing_create, name='mailing_create'),
    path('mailings/<int:pk>/update/', views.mailing_update, name='mailing_update'),
    path('mailings/<int:pk>/delete/', views.mailing_delete, name='mailing_delete'),
    path('mailings/<int:pk>/send/', views.mailing_send, name='mailing_send'),
    path('mailings/<int:pk>/disable/', views.mailing_disable, name='mailing_disable'),
    # Попытки рассылок
    path('mailings/<int:mailing_id>/attempts/', views.MailingAttemptListView.as_view(), name='mailing_attempts'),
    path('attempts/', views.MailingAttemptListView.as_view(), name='attempt_list'),
    # Статистика
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    # Аутентификация
    path('login/', auth_views.user_login, name='login'),  # Убедитесь, что этот маршрут присутствует
    path('logout/', auth_views.user_logout, name='logout'),
    path('register/', auth_views.register, name='register'),
    path('activate/<uidb64>/<token>/', auth_views.activate, name='activate'),
    path('password_reset/', auth_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    # Пользователи (для менеджеров)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/block/', views.user_block, name='user_block'),
]
