# Generated by Django 5.1.6 on 2025-02-27 09:53

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clients", "0003_mailing"),
    ]

    operations = [
        migrations.CreateModel(
            name="MailingAttempt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "attempt_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Дата и время попытки",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("successful", "Успешно"), ("failed", "Не успешно")],
                        max_length=10,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "server_response",
                    models.TextField(verbose_name="Ответ почтового сервера"),
                ),
                (
                    "mailing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="clients.mailing",
                        verbose_name="Рассылка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Попытка рассылки",
                "verbose_name_plural": "Попытки рассылок",
            },
        ),
    ]
