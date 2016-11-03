from django.core.management.base import BaseCommand, CommandError

from basin3d.models import DataSource


class Command(BaseCommand):
    help = 'Get the credential format.'

    def add_arguments(self, parser):
        parser.add_argument('datasource_id', type=str)

    def handle(self, *args, **options):
        datasource_id = options['datasource_id']
        try:
            datasource = DataSource.objects.get(name=datasource_id)
            self.stdout.write(datasource.plugin.get_plugin().datasource_credentials_format)
        except DataSource.DoesNotExist:
            raise CommandError('DataSource "%s" does not exist' % datasource_id)
