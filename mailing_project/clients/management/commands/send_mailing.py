from django.core.management.base import BaseCommand, CommandError
from clients.models import Mailing


class Command(BaseCommand):
    help = 'Отправляет рассылку по её ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки для отправки')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
            if mailing.send_mailing():
                self.stdout.write(self.style.SUCCESS(f'Рассылка {mailing_id} успешно отправлена'))
            else:
                self.stdout.write(
                    self.style.ERROR(f'Нельзя отправить рассылку {mailing_id}: завершена или время истекло'))
        except Mailing.DoesNotExist:
            raise CommandError(f'Рассылка с ID {mailing_id} не найдена')
        except Exception as e:
            raise CommandError(f'Ошибка при отправке: {str(e)}')
