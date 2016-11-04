from basin3d.tests import configure

# Load test settings
configure()

from django.test import TestCase
from basin3d.synthesis.models import simulations, Region


class RegionTests(TestCase):
    def test_create(self):
        """ Test Region Creation"""

        a_region = Region(name="a site",
                          id="SI123",
                          description="This is for my site description", )

        self.assertEqual("a site", a_region.name)
        self.assertEqual("SI123", a_region.id)
        self.assertEqual("This is for my site description", a_region.description)


class Model(TestCase):
    def test_create(self):
        obj = simulations.Model(id="1234", version="1.0", dimensionality="1D", url="/testserver/url")

        self.assertEqual("1234", obj.id)
        self.assertEqual("1.0", obj.version)
        self.assertEqual("1D", obj.dimensionality)
        self.assertEqual("/testserver/url", obj.url)


class ModelDomain(TestCase):
    def test_create(self):
        obj = simulations.ModelDomain(model_domain_id="1234",
                                      model_domain_name="a model domain",
                                      url="/testserver/url",
                                      geom={},
                                      meshes=[simulations.Mesh(mesh_id="1",
                                                               parameters=[],
                                                               initial_conditions=[])])

        self.assertEqual("1234", obj.model_domain_id)
        self.assertEqual("a model domain", obj.model_domain_name)
        self.assertEqual("/testserver/url", obj.url)
        self.assertEqual({}, obj.geom)
        self.assertEqual([simulations.Mesh(mesh_id="1",
                                           parameters=[],
                                           initial_conditions=[])], obj.meshes)
