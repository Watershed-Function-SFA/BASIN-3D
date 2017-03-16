from basin3d.synthesis.models import simulations
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


class Model(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_create(self):
        obj = simulations.Model(self.datasource, id="1234", version="1.0", dimensionality="1D",
                                web_location="/testserver/url")

        self.assertEqual("A-1234", obj.id)
        self.assertEqual("1.0", obj.version)
        self.assertEqual("1D", obj.dimensionality)
        self.assertEqual("/testserver/url", obj.web_location)


class ModelDomain(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_create(self):
        obj = simulations.ModelDomain(self.datasource, id="1234",
                                      name="a model domain",
                                      geom={})

        self.assertEqual("A-1234", obj.id)
        self.assertEqual("a model domain", obj.name)
        self.assertEqual({}, obj.geom)
