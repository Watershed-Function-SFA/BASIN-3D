import basin3d.synthesis.models.field
from basin3d.synthesis.models import Person

import json

from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from basin3d.synthesis import models

from basin3d.models import DataSource
from basin3d.synthesis.serializers import RegionSerializer, SiteSerializer


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
                          "url": None})


class SiteSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_serializer(self):
        """ Test  Serialization"""

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
                                                 "units": "DD"},
                          "contacts": [{"first_name": "Barry", "last_name": "Allen",
                                        "email": "ballen@foo.bar", "institution": "DC Comics"}],
                          "pi": {"first_name": "Jessica", "last_name": "Jones",
                                 "email": "jjones@foo.bar", "institution": "DC Comics"},
                          "urls": ["http://foo.bar"],
                          "url": None}
                         )
