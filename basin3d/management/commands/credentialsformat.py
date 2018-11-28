from basin3d.models import DataSource
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Get the credential format.'

    def add_arguments(self, parser):
        parser.add_argument('datasource_id', type=str)

    def handle(self, *args, **options):
        datasource_id = options['datasource_id']
        try:
            datasource = DataSource.objects.get(name=datasource_id)
            if hasattr(datasource.get_plugin().get_meta(), "connection_class"):
                self.stdout.write(
                    datasource.get_plugin().get_meta().connection_class.get_credentials_format())
            else:
                self.stdout.write("There is no credentials format set.")
                self.stdout.write("Set 'connection_class' in {}.{}.DataSourceMeta".format(
                    datasource.plugin_module, datasource.plugin_class))
        except DataSource.DoesNotExist:
            raise CommandError('DataSource "%s" does not exist' % datasource_id)
