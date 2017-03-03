import basin3d.synthesis.models.field
from basin3d.synthesis.models import Person
from basin3d.tests import configure

# Load test settings
configure()
import json

from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from basin3d.synthesis import models

from basin3d.models import DataSource
from basin3d.synthesis.serializers import RegionSerializer, ModelSerializer, ModelDomainSerializer, \
    MeshSerializer, \
    SiteSerializer


class RegionSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_serializer(self):
        """ Test Regions Serialization"""

        a_region = basin3d.synthesis.models.field.Region(self.datasource, name="a region",
                                                         id="SI123",
                                                         description="US",
                                                         geom={})

        s = RegionSerializer(a_region)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"id": "A-SI123", "description": "US", "geom": {}, 'name': 'a region',
                          "url": None,
                          'model_domains': None})


class ModelSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_serializer(self):
        """ Test Model Serialization"""

        a_region = models.simulations.Model(self.datasource, version="1.0", id="M1",
                                            dimensionality="1D")

        s = ModelSerializer(a_region)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {'dimensionality': '1D', 'name': None, 'version': "1.0", 'id': 'A-M1',
                          'url': None,
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
                models.simulations.ModelParameter(self.datasource, id=num,
                                                  data_source_name="foo_{}".format(num),
                                                  model_name="param_{}".format(num),
                                                  value=float(1 / (num + 1))))

        obj = models.simulations.Mesh(self.datasource, id="ME1", parameters=model_parameters,
                                      initial_conditions=[])

        s = MeshSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"id": "A-ME1", "parameters": [
                             {"id": "A-0", "model_name": "param_0", "data_source_name": "foo_0",
                              "value": 1.0},
                             {"id": "A-1", "model_name": "param_1", "data_source_name": "foo_1",
                              "value": 0.5},
                             {"id": "A-2", "model_name": "param_2", "data_source_name": "foo_2",
                              "value": 0.3333333333333333},
                             {"id": "A-3", "model_name": "param_3", "data_source_name": "foo_3",
                              "value": 0.25},
                             {"id": "A-4", "model_name": "param_4", "data_source_name": "foo_4",
                              "value": 0.2}], "initial_conditions": [], "geom": {}, "url": None})


class SiteSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_serializer(self):
        """ Test Mesh Serialization"""

        obj = models.field.Site(self.datasource, id=1, name="Foo",
                                description="Foo Bar Site",
                                country="US",
                                state_province="California",
                                utc_offset=-6,
                                center_coordinates=basin3d.synthesis.models.field.GeographicCoordinate(
                                    x=90.0,
                                    y=90.0,
                                    datum=models.field.GeographicCoordinate.DATUM_WGS84,
                                    units=models.field.GeographicCoordinate.UNITS_DEC_DEGREES
                                ),
                                pi=Person(first_name="Jessica",
                                          last_name="Jones",
                                          email="jjones@foo.bar",
                                          institution="DC Comics"),
                                contacts=[Person(first_name="Barry",
                                                 last_name="Allen",
                                                 email="ballen@foo.bar",
                                                 institution="DC Comics")],
                                urls=["http://foo.bar"])

        s = SiteSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.maxDiff = None
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"id": "A-1",
                          "name": "Foo",
                          "description": "Foo Bar Site",
                          "type": "site",
                          "country": "US",
                          "state_province": "California",
                          "utc_offset": -6,
                          "center_coordinates": {"datum": "WGS84", "type": "geographic",
                                                 "latitude": 90.0, "longitude": 90.0,
                                                 "units": "DD"}, "geom": None,
                          "contacts": [{"first_name": "Barry", "last_name": "Allen",
                                        "email": "ballen@foo.bar", "institution": "DC Comics"}],
                          "pi": {"first_name": "Jessica", "last_name": "Jones",
                                 "email": "jjones@foo.bar", "institution": "DC Comics"},
                          "urls": ["http://foo.bar"],
                          "url": None}
                         )
