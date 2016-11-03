from django.core.management.base import BaseCommand, CommandError

from basin3d.models import DataSource


class Command(BaseCommand):
    help = 'Shows the credentials for the specified DataSource'

    def add_arguments(self, parser):
        parser.add_argument('datasource_id', type=str)

    def handle(self, *args, **options):
        datasource_id = options['datasource_id']
        try:
            datasource = DataSource.objects.get(name=datasource_id)
            self.stdout.write(datasource.credentials)
        except DataSource.DoesNotExist:
            raise CommandError('DataSource "%s" does not exist' % datasource_id)
