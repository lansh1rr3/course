from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from .models import Mailing, MailingStatistics, send_mailing


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('subject', 'status', 'start_datetime', 'end_datetime', 'send_button')
    list_filter = ('status',)
    actions = ['send_mailing']

    def send_button(self, obj):
        return format_html('<a class="button" href="{}">Отправить</a>', f'/admin/mailing/{obj.id}/send/')

    send_button.short_description = "Действия"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<pk>/send/', self.admin_site.admin_view(self.send_mailing_view), name='mailing-send'),
        ]
        return custom_urls + urls

    def send_mailing_view(self, request, pk):
        mailing = Mailing.objects.get(pk=pk)
        send_mailing(mailing)
        self.message_user(request, f"Рассылка {mailing.subject} запущена!")
        return redirect('admin:mailing_mailing_changelist')


@admin.register(MailingStatistics)
class MailingStatisticsAdmin(admin.ModelAdmin):
    list_display = ("mailing", "recipient", "sent_at", "status")
    list_filter = ("status", "sent_at")
    search_fields = ("recipient", "mailing__id")
