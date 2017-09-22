from basin3d.tests import configure

# Load test settings
configure()

from django.test import TestCase
from basin3d.models import DataSource
from basin3d.synthesis.models.field import Region


class RegionTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_create(self):
        """ Test Region Creation"""

        a_region = Region(self.datasource, name="a site",
                          id="SI123",
                          description="This is for my site description", )

        self.assertEqual("a site", a_region.name)
        self.assertEqual("A-SI123", a_region.id)
        self.assertEqual("This is for my site description", a_region.description)

