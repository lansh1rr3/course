from django.utils import timezone
from django.core.mail import send_mail
from django.db import models
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MailingStatistics(models.Model):
    mailing = models.ForeignKey("Mailing", on_delete=models.CASCADE, related_name="statistics")
    sent_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ("success", "Успешно"),
        ("failed", "Ошибка"),
        ("pending", "В ожидании"),
    ], default="pending")
    recipient = models.EmailField()
    response_message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Статистика рассылки"
        verbose_name_plural = "Статистика рассылок"

    def __str__(self):
        return f"{self.mailing} → {self.recipient} ({self.status})"


class Client(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=100, verbose_name='Name')
    comment = models.TextField(max_length=100, verbose_name='Description')
    owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True,
                              blank=True)

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'

    def __str__(self):
        return self.full_name


class Message(models.Model):
    subject = models.CharField("Тема", max_length=255)
    body = models.TextField("Тело сообщения")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class MailingStatus(models.TextChoices):
    CREATED = 'Создана', 'Создана'
    STARTED = 'Запущена', 'Запущена'
    FINISHED = 'Завершена', 'Завершена'


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    subject = models.CharField(max_length=255, blank=True, null=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')
    message = models.ForeignKey('Message', on_delete=models.CASCADE)
    recipients = models.ManyToManyField('Recipient')
    owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True, blank=True)

    def get_recipients(self):
        return Client.objects.all()

    def __str__(self):
        return f"Mailing {self.subject} - {self.status}"

    def update_status(self):
        now_time = timezone.now()
        if now_time < self.start_datetime:
            self.status = 'created'
        elif self.start_datetime <= now_time <= self.end_datetime:
            if self.status != 'started':
                self.status = 'started'
        elif now_time > self.end_datetime:
            self.status = 'completed'
        self.save()

    def complete_sending(self):
        self.status = 'completed'
        self.save()

    def update_statistics(self):
        attempts = DeliveryAttempt.objects.filter(mailing=self)
        total_attempts = attempts.count()
        successful_attempts = attempts.filter(status='success').count()
        failed_attempts = attempts.filter(status='failed').count()
        sent_messages = successful_attempts

        stats, created = MailingStatistics.objects.get_or_create(mailing=self)
        stats.total_attempts = total_attempts
        stats.successful_attempts = successful_attempts
        stats.failed_attempts = failed_attempts
        stats.sent_messages = sent_messages
        stats.status = 'success' if successful_attempts > 0 and failed_attempts == 0 else 'failed' if failed_attempts > 0 else 'pending'
        stats.save()


def send_mailing(mailing):
    recipients = mailing.recipients.all()
    logger.info(f"Начинаем отправку для {len(recipients)} получателей")

    for recipient in recipients:
        try:
            logger.info(f"Отправка на {recipient.email}")
            send_mail(
                mailing.message.subject,
                mailing.message.body,
                settings.DEFAULT_FROM_EMAIL,
                [recipient.email],
                fail_silently=False,
            )
            logger.info(f"Успешно отправлено на {recipient.email}")
            DeliveryAttempt.create_attempt(mailing, recipient, 'success', 'Email sent successfully')
        except Exception as e:
            logger.error(f"Ошибка для {recipient.email}: {str(e)}")
            DeliveryAttempt.create_attempt(mailing, recipient, 'failed', str(e))

    mailing.complete_sending()
    mailing.update_statistics()


class DeliveryAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    attempt_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    server_response = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Attempt {self.id} - {self.status} for Mailing {self.mailing.id} to {self.recipient.email}"

    @staticmethod
    def create_attempt(mailing, recipient, status, response=None):
        try:
            attempt = DeliveryAttempt(
                mailing=mailing,
                recipient=recipient,
                status=status,
                server_response=response
            )
            attempt.save()
            logger.info(f"Успешно создана запись DeliveryAttempt с ID: {attempt.id}")
            return attempt
        except Exception as e:
            logger.error(f"Ошибка при создании записи DeliveryAttempt: {str(e)}")
            raise
