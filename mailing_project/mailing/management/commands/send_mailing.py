from django.core.management.base import BaseCommand
from mailing.models import Mailing
from mailing.tasks import send_mailing_task


class Command(BaseCommand):
    help = "Отправка рассылки вручную"

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help="ID рассылки")

    def handle(self, *args, **kwargs):
        mailing_id = kwargs['mailing_id']
        mailing = Mailing.objects.get(id=mailing_id)
        send_mailing_task(mailing.id)
        self.stdout.write(self.style.SUCCESS(f"Рассылка {mailing.subject} запущена!"))
