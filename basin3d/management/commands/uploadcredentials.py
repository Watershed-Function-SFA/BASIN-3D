from django.core.management.base import BaseCommand, CommandError

from basin3d.models import DataSource


class Command(BaseCommand):
    help = """Uploads the credentials for the specified DataSource from standard input."""

    def add_arguments(self, parser):
        parser.add_argument('datasource_id', type=str)

    def handle(self, *args, **options):
        datasource_id = options['datasource_id']
        try:
            datasource = DataSource.objects.get(name=datasource_id)
            import sys
            data = sys.stdin.read()
            datasource.credentials = data
            datasource.save()

            self.stdout.write(
                self.style.SUCCESS("Credentials have been uploaded to Data Source '{}'".format(datasource_id)))
        except DataSource.DoesNotExist:
            raise CommandError('DataSource "%s" does not exist' % datasource_id)
