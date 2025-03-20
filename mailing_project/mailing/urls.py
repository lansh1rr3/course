from django.urls import path
from .views import (
    MailingListView, MailingDetailView, MailingCreateView, MailingUpdateView, MailingDeleteView,
    MessageListView, MessageDetailView, MessageCreateView, MessageUpdateView, MessageDeleteView,
    mailing_statistics_list, RecipientListView, RecipientDetailView, RecipientCreateView,
    RecipientUpdateView, RecipientDeleteView, mailing_statistics_detail, SendMailingView, MailingHomeView,
    disable_mailing
)

app_name = 'mailing'

urlpatterns = [
    path('mailing/', MailingListView.as_view(), name='mailing_list'),
    path('mailing/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailing/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailing/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailing/recipients/', RecipientListView.as_view(), name='recipient_list'),
    path('mailing/recipients/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('mailing/recipients/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('mailing/recipients/<int:pk>/update/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('mailing/recipients/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('mailing/<int:pk>/send/', SendMailingView.as_view(), name='send_mailing'),
    path('mailing/<int:mailing_id>/statistics/', mailing_statistics_detail, name='mailing_statistics_detail'),
    path('mailing/statistics/', mailing_statistics_list, name='mailing_statistics'),
    path('mailing/<int:mailing_id>/disable/', disable_mailing, name='disable_mailing'),
    path('', MailingHomeView.as_view(), name='home'),
]
