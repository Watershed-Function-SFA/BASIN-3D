import json

from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from basin3d.synthesis import models
from basin3d.synthesis.serializers import SiteSerializer, LocationSerializer, DataPointSerializer


class SiteSerializerTests(TestCase):
    def test_serializer(self):
        """ Test Sites Serialization"""

        a_site = models.Site(name="a site", site_id="SI123", country="US",
                             state_province="CA", geom="[]",
                             contact_name="David Gruber", contact_email="gruber@david.com",
                             contact_institution="Museum of Natural History")

        s = SiteSerializer(a_site)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"site_id": "SI123", "country": "US", "contact_name": "David Gruber",
                          "contact_email": "gruber@david.com", "contact_institution": "Museum of Natural History",
                          "urls": [], "geom": "[]", "site": None}

                         )


class LocationSerializerTests(TestCase):
    def test_create(self):
        """ Test Location Serialization"""

        a_loc = models.Location(site_id="SI123", location_id="ER984375", site="http://example.com/url/SI123",
                                group="agroup", geom={"latitude": 38, "longitude": 140, "elevation": 55},
                                type="TBD")

        s = LocationSerializer(a_loc)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"site_id": "SI123",
                          "site": None,
                          "location_id": "ER984375",
                          "name": None,
                          "measure_variables": [],
                          "group": "agroup",
                          "type": "TBD",
                          "geom": {"latitude": 38, "elevation": 55, "longitude": 140}}
                         )


class DataPointSerializerTests(TestCase):
    def test_create(self):
        """ Test Location Serialization"""

        a_loc = models.DataPoint(type="foo", location_id="SFGSDF", site_id="FODOJF",
                                 depth=9.342484538, timestamp='2016-10-17T21:52:10.016788', value=9.38734568,
                                 unit="aunit",
                                 average="average")

        s = DataPointSerializer(a_loc)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"type": "foo", "location_id": "SFGSDF", "depth": 9.342484538,
                          "timestamp": "2016-10-17T21:52:10.016788", "value": 9.38734568, "unit": "aunit",
                          "average": "average", "site": None})
