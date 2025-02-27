from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User
from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm


def is_manager(user):
    return user.groups.filter(name='managers').exists()


# Клиенты
@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(300), name='dispatch')
class ClientListView(ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'profile') or not user.profile.is_active:
            messages.error(self.request, 'Ваш аккаунт заблокирован.')
            return Client.objects.none()
        if is_manager(user):
            return Client.objects.all()
        return Client.objects.filter(mailing__user=user).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = is_manager(self.request.user)
        return context


@login_required
def client_create(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
        messages.error(request, 'Ваш аккаунт заблокирован.')
        return redirect('login')
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            if not is_manager(request.user):
                client.mailing_set.add(Mailing.objects.get(user=request.user))
            client.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'clients/client_form.html', {'form': form})


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
        messages.error(request, 'Ваш аккаунт заблокирован.')
        return redirect('login')
    if not is_manager(request.user) and client.mailing_set.filter(user=request.user).count() == 0:
        messages.error(request, 'У вас нет прав для редактирования этого клиента.')
        return redirect('client_list')
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/client_form.html', {'form': form})


@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
        messages.error(request, 'Ваш аккаунт заблокирован.')
        return redirect('login')
    if not is_manager(request.user) and client.mailing_set.filter(user=request.user).count() == 0:
        messages.error(request, 'У вас нет прав для удаления этого клиента.')
        return redirect('client_list')
    if request.method == 'POST':
        client.delete()
        return redirect('client_list')
    return render(request, 'clients/client_confirm_delete.html', {'client': client})


@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(300), name='dispatch')
class MessageListView(ListView):
    model = Message
    template_name = 'clients/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'profile') or not user.profile.is_active:
            messages.error(self.request, 'Ваш аккаунт заблокирован.')
            return Message.objects.none()
        if is_manager(user):
            return Message.objects.all()
        return Message.objects.filter(mailing__user=user).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = is_manager(self.request.user)
        return context


@login_required
def message_create(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
        messages.error(request, 'Ваш аккаунт заблокирован.')
        return redirect('login')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            if not is_manager(request.user):
                message.mailing_set.add(Mailing.objects.get(user=request.user))
            message.save()
            return redirect('message_list')
    else:
        form = MessageForm()
    return render(request, 'clients/message_form.html', {'form': form})


@login_required
def message_update(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
        messages.error(request, 'Ваш аккаунт заблокирован.')
        return redirect('login')
    if not is_manager(request.user) and message.mailing_set.filter(user=request.user).count() == 0:
        messages.error(request, 'У вас нет прав для редактирования этого сообщения.')
        return redirect('message_list')
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('message_list')
    else:
        form = MessageForm(instance=message)
    return render(request, 'clients/message_form.html', {'form': form})


@login_required
def message_delete(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
        messages.error(request, 'Ваш аккаунт заблокирован.')
        return redirect('login')
    if not is_manager(request.user) and message.mailing_set.filter(user=request.user).count() == 0:
        messages.error(request, 'У вас нет прав для удаления этого сообщения.')
        return redirect('message_list')
    if request.method == 'POST':
        message.delete()
        return redirect('message_list')
    return render(request, 'clients/message_confirm_delete.html', {'message': message})


@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(300), name='dispatch')
class MailingListView(ListView):
    model = Mailing
    template_name = 'clients/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'profile') or not user.profile.is_active:
            messages.error(self.request, 'Ваш аккаунт заблокирован.')
            return Mailing.objects.none()
        if is_manager(user):
            return Mailing.objects.all()
        return Mailing.objects.filter(user=user, is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = is_manager(self.request.user)
        return context


@login_required
def mailing_create(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
        messages.error(request, 'Ваш аккаунт заблокирован.')
        return redirect('login')
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.user = request.user
            mailing.is_active = True
            mailing.save()
            form.save_m2m()
            return redirect('mailing_list')
    else:
        form = MailingForm()
    return render(request, 'clients/mailing_form.html', {'form': form})


@login_required
def mailing_update(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
        messages.error(request, 'Ваш аккаунт заблокирован.')
        return redirect('login')
    if not is_manager(request.user) and mailing.user != request.user:
        messages.error(request, 'У вас нет прав для редактирования этой рассылки.')
        return redirect('mailing_list')
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.user = request.user
            mailing.save()
            form.save_m2m()
            return redirect('mailing_list')
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'clients/mailing_form.html', {'form': form})


@login_required
def mailing_delete(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
        messages.error(request, 'Ваш аккаунт заблокирован.')
        return redirect('login')
    if not is_manager(request.user) and mailing.user != request.user:
        messages.error(request, 'У вас нет прав для удаления этой рассылки.')
        return redirect('mailing_list')
    if request.method == 'POST':
        mailing.delete()
        return redirect('mailing_list')
    return render(request, 'clients/mailing_confirm_delete.html', {'mailing': mailing})


@login_required
def mailing_send(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
        messages.error(request, 'Ваш аккаунт заблокирован.')
        return redirect('login')
    if not is_manager(request.user) and mailing.user != request.user:
        messages.error(request, 'У вас нет прав для отправки этой рассылки.')
        return redirect('mailing_list')
    if request.method == 'POST':
        try:
            if mailing.send_mailing():
                messages.success(request, 'Рассылка успешно отправлена.')
            else:
                messages.error(request,
                               'Нельзя отправить завершенную или отключённую рассылку или время отправки истекло.')
        except Exception as e:
            messages.error(request, f'Ошибка при отправке: {str(e)}')
        return redirect('mailing_list')
    return render(request, 'clients/mailing_confirm_send.html', {'mailing': mailing})


@login_required
def mailing_disable(request, pk):
    if not is_manager(request.user):
        messages.error(request, 'У вас нет прав для отключения рассылок.')
        return redirect('mailing_list')
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        mailing.is_active = False
        mailing.status = 'disabled'
        mailing.save()
        messages.success(request, 'Рассылка отключена.')
        return redirect('mailing_list')
    return render(request, 'clients/mailing_confirm_disable.html', {'mailing': mailing})


@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(300), name='dispatch')
class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = 'clients/mailing_attempt_list.html'
    context_object_name = 'attempts'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
            messages.error(request, 'Ваш аккаунт заблокирован.')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        mailing_id = self.kwargs.get('mailing_id')
        if mailing_id:
            mailing = get_object_or_404(Mailing, pk=mailing_id)
            if not is_manager(user) and mailing.user != user:
                messages.error(self.request, 'У вас нет прав для просмотра попыток этой рассылки.')
                return MailingAttempt.objects.none()
            return MailingAttempt.objects.filter(mailing_id=mailing_id)
        if is_manager(user):
            return MailingAttempt.objects.all()
        return MailingAttempt.objects.filter(mailing__user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = is_manager(self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(300), name='dispatch')
class StatisticsView(ListView):
    template_name = 'clients/statistics.html'
    context_object_name = 'stats'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
            messages.error(request, 'Ваш аккаунт заблокирован.')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if is_manager(user):
            mailings = Mailing.objects.all()
        else:
            mailings = Mailing.objects.filter(user=user, is_active=True)
        attempts = MailingAttempt.objects.filter(mailing__in=mailings)

        stats = {
            'total_mailings': mailings.count(),
            'successful_attempts': attempts.filter(status='successful').count(),
            'failed_attempts': attempts.filter(status='failed').count(),
            'total_attempts': attempts.count(),
            'messages_sent': sum(
                mailing.clients.count() for mailing in mailings if mailing.status in ['started', 'completed']),
        }
        return [stats]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = is_manager(self.request.user)
        context['user'] = self.request.user
        return context


@method_decorator(login_required, name='dispatch')
class UserListView(ListView):
    model = User
    template_name = 'clients/user_list.html'
    context_object_name = 'users'

    def dispatch(self, request, *args, **kwargs):
        if not is_manager(request.user):
            messages.error(request, 'У вас нет прав для просмотра списка пользователей.')
            return redirect('client_list')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return User.objects.all()


@login_required
def user_block(request, pk):
    if not is_manager(request.user):
        messages.error(request, 'У вас нет прав для блокировки пользователей.')
        return redirect('client_list')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.profile.is_active = not user.profile.is_active
        user.profile.save()
        status = 'заблокирован' if not user.profile.is_active else 'разблокирован'
        messages.success(request, f'Пользователь {user.username} {status}.')
        return redirect('user_list')

    return render(request, 'clients/user_confirm_block.html', {'user': user})
