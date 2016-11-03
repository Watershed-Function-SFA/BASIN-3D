from django.test import TestCase

from basin3d.synthesis import models


class SiteTests(TestCase):
    def test_create(self):
        """ Test Sites Creation"""

        a_site = models.Site(name="a site", site_id="SI123", country="US",
                             state_province="CA", geom="[]",
                             contact_name="David Gruber", contact_email="gruber@david.com",
                             contact_institution="Museum of Natural History")

        self.assertEqual("a site", a_site.name)
        self.assertEqual("SI123", a_site.site_id)
        self.assertEqual("US", a_site.country)
        self.assertEqual("CA", a_site.state_province)
        self.assertEqual("David Gruber", a_site.contact_name)
        self.assertEqual("gruber@david.com", a_site.contact_email)
        self.assertEqual("Museum of Natural History", a_site.contact_institution)


class LocationTests(TestCase):
    def test_create(self):
        """ Test Sites Creation"""

        a_loc = models.Location(site_id="SI123", location_id="ER984375", data_source_id=1,
                                group="agroup", geom={"latitude": 38, "longitude": 140, "elevation": 55},
                                type="TBD")

        self.assertEqual("SI123", a_loc.site_id)
        self.assertEqual("ER984375", a_loc.location_id)
        self.assertEqual(1, a_loc.data_source_id)
        self.assertEqual("agroup", a_loc.group)
        self.assertEqual({"latitude": 38, "longitude": 140, "elevation": 55}, a_loc.geom)
        self.assertEqual("TBD", a_loc.type)
