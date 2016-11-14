import basin3d.synthesis.models.field
from basin3d.tests import configure

# Load test settings
configure()
import json

from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from basin3d.synthesis import models
from basin3d.synthesis.serializers import RegionSerializer, ModelSerializer, ModelDomainSerializer, MeshSerializer


class RegionSerializerTests(TestCase):
    def test_serializer(self):
        """ Test Regions Serialization"""

        a_region = basin3d.synthesis.models.field.Region(name="a site", id="SI123", description="US", geom={})

        s = RegionSerializer(a_region)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"id": "SI123", "description": "US", "geom": {}, "url": None})


class ModelSerializerTests(TestCase):
    def test_serializer(self):
        """ Test Model Serialization"""

        a_region = models.simulations.Model(verion="1.0", id="M1", dimensionality="1D")

        s = ModelSerializer(a_region)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {'dimensionality': '1D', 'version': None, 'id': 'M1', 'url': None})


class ModelDomainSerializerTests(TestCase):
    def test_serializer(self):
        """ Test Model Domain Serialization"""

        a_region = models.simulations.ModelDomain(model_domain_name="a model domain",
                                                  model_domain_id="SI123",
                                                  meshes=[], geom={})

        s = ModelDomainSerializer(a_region)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {'geom': {},
                          'meshes': [],
                          'model_domain_id': 'SI123',
                          'model_domain_name': 'a model domain',
                          'url': None})


class MeshSerializerTests(TestCase):
    def test_serializer(self):
        """ Test Mesh Serialization"""

        model_parameters = []
        for num in range(5):
            model_parameters.append(
                models.simulations.ModelParameter(id=num, name="param_{}".format(num), value=float(1 / (num + 1))))

        obj = models.simulations.Mesh(mesh_id="ME1", parameters=model_parameters, initial_conditions=[])

        s = MeshSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"mesh_id": "ME1", "parameters": [{"id": "0", "name": "param_0", "value": 1.0, "url": None},
                                                           {"id": "1", "name": "param_1", "value": 0.5, "url": None},
                                                           {"id": "2", "name": "param_2", "value": 0.3333333333333333,
                                                            "url": None},
                                                           {"id": "3", "name": "param_3", "value": 0.25, "url": None},
                                                           {"id": "4", "name": "param_4", "value": 0.2, "url": None}],
                          "initial_conditions": []})
