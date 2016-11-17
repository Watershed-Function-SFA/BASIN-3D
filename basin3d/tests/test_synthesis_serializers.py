import basin3d.synthesis.models.field
from basin3d.tests import configure

# Load test settings
configure()
import json

from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from basin3d.synthesis import models

from basin3d.models import DataSource
from basin3d.synthesis.serializers import RegionSerializer, ModelSerializer, ModelDomainSerializer, MeshSerializer


class RegionSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_serializer(self):
        """ Test Regions Serialization"""

        a_region = basin3d.synthesis.models.field.Region(self.datasource, name="a site", id="SI123", description="US",
                                                         geom={})

        s = RegionSerializer(a_region)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"id": "A-SI123", "description": "US", "geom": {}, 'name': 'a site', "url": None})


class ModelSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_serializer(self):
        """ Test Model Serialization"""

        a_region = models.simulations.Model(self.datasource, verion="1.0", id="M1", dimensionality="1D")

        s = ModelSerializer(a_region)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {'dimensionality': '1D', 'name': None, 'version': None, 'id': 'A-M1', 'url': None,
                          'web_location': None})


class ModelDomainSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_serializer(self):
        """ Test Model Domain Serialization"""

        a_region = models.simulations.ModelDomain(self.datasource, name="a model domain",
                                                  id="SI123", geom={})

        s = ModelDomainSerializer(a_region)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {'geom': {},
                          'meshes': None,
                          'id': 'A-SI123',
                          'name': 'a model domain',
                          'url': None})


class MeshSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_serializer(self):
        """ Test Mesh Serialization"""

        model_parameters = []
        for num in range(5):
            model_parameters.append(
                models.simulations.ModelParameter(self.datasource, id=num, name="param_{}".format(num),
                                                  value=float(1 / (num + 1))))

        obj = models.simulations.Mesh(self.datasource, id="ME1", parameters=[], initial_conditions=[])

        s = MeshSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"id": "A-ME1", "parameters": [], "geom": {},
                          "initial_conditions": [], "url": None})
