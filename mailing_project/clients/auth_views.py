from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from .models import UserProfile


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'clients/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'clients/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email уже зарегистрирован.')
            return render(request, 'clients/register.html')

        user = User.objects.create_user(username=username, email=email, password=password, is_active=False)

        UserProfile.objects.create(user=user, is_active=False)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        confirmation_link = f"{settings.SITE_URL}/activate/{uid}/{token}/"

        subject = 'Подтверждение регистрации'
        message = render_to_string('clients/activation_email.html', {
            'user': user,
            'confirmation_link': confirmation_link,
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], html_message=message)

        messages.success(request, 'Регистрация прошла успешно. Проверьте email для подтверждения.')
        return redirect('login')

    return render(request, 'clients/register.html')


def activate(request, uidb64, token):
    from django.utils.http import urlsafe_base64_decode
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        user.profile.is_active = True
        user.profile.save()
        messages.success(request, 'Ваш аккаунт активирован. Теперь вы можете войти.')
        return redirect('login')
    else:
        messages.error(request, 'Ссылка для активации недействительна.')
        return redirect('login')


@login_required
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user, is_active=True)
            if not user.profile.is_active:
                messages.error(request, 'Ваш аккаунт заблокирован.')
                return redirect('login')
            login(request, user)
            return redirect('client_list')
    else:
        form = AuthenticationForm()
    return render(request, 'clients/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'clients/password_reset.html'
    email_template_name = 'clients/password_reset_email.html'
    success_url = '/password_reset/done/'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'clients/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'clients/password_reset_confirm.html'
    success_url = '/password_reset/complete/'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'clients/password_reset_complete.html'
