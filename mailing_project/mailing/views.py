from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
# Исправляем импорт cache_page
from django.views.decorators.cache import cache_page
from .models import Recipient, Message, Mailing, DeliveryAttempt, MailingStatistics, send_mailing
from .forms import RecipientForm, MessageForm, MailingForm
from django.urls import reverse_lazy
from django.http import JsonResponse
import os
from dotenv import load_dotenv

load_dotenv()


class UserIsOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_manager():
            return True
        obj = self.get_object()
        return obj.owner == self.request.user if hasattr(obj, 'owner') else False

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для выполнения этого действия.")
        return redirect('mailing:home')


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'

    def get_queryset(self):
        if self.request.user.is_manager():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, UserIsOwnerMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UserIsOwnerMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')


class MailingDeleteView(LoginRequiredMixin, UserIsOwnerMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailing/recipient_list.html'

    def get_queryset(self):
        if self.request.user.is_manager():
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=self.request.user)


class RecipientDetailView(LoginRequiredMixin, UserIsOwnerMixin, DetailView):
    model = Recipient
    template_name = 'mailing/recipient_detail.html'


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UserIsOwnerMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipient_list')


class RecipientDeleteView(LoginRequiredMixin, UserIsOwnerMixin, DeleteView):
    model = Recipient
    template_name = 'mailing/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'

    def get_queryset(self):
        if self.request.user.is_manager():
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, UserIsOwnerMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UserIsOwnerMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageDeleteView(LoginRequiredMixin, UserIsOwnerMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')


class MailingHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'mailing/home.html'


class SendMailingView(LoginRequiredMixin, UserIsOwnerMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        try:
            send_mailing(mailing)
            messages.success(request, f"Рассылка {mailing.subject} запущена!")
        except Exception as e:
            messages.error(request, f"Ошибка при запуске рассылки: {str(e)}")
        return redirect('mailing:mailing_detail', pk=pk)


@cache_page(300)
def mailing_statistics_list(request):
    if not request.user.is_authenticated:
        return redirect('users:login')
    if request.user.is_manager():
        statistics = MailingStatistics.objects.all().order_by("-sent_at")
    else:
        statistics = MailingStatistics.objects.filter(mailing__owner=request.user).order_by("-sent_at")
    return render(request, "mailing/statistics_list.html", {"statistics": statistics})


@cache_page(300)
def mailing_statistics_detail(request, mailing_id):
    if not request.user.is_authenticated:
        return redirect('users:login')
    mailing = get_object_or_404(Mailing, id=mailing_id)
    if not request.user.is_manager() and mailing.owner != request.user:
        messages.error(request, "У вас нет прав для просмотра этой статистики.")
        return redirect('mailing:mailing_list')
    statistics = MailingStatistics.objects.filter(mailing=mailing)
    attempts = DeliveryAttempt.objects.filter(mailing=mailing)
    return render(request, 'mailing/statistics_detail.html', {
        'mailing': mailing,
        'statistics': statistics,
        'attempts': attempts,
    })


@login_required
def disable_mailing(request, mailing_id):
    if not request.user.is_manager():
        messages.error(request, "У вас нет прав для отключения рассылок.")
        return redirect('mailing:mailing_list')
    mailing = get_object_or_404(Mailing, id=mailing_id)
    mailing.status = 'completed'
    mailing.save()
    messages.success(request, f"Рассылка {mailing.subject} отключена.")
    return redirect('mailing:mailing_list')
