from basin3d.synthesis.models import Person

import json

from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from basin3d.synthesis import models
from basin3d.serializers import ObservedPropertySerializer
from basin3d.models import DataSource, GeographicalGroup, ObservedProperty, \
    ObservedPropertyVariable, SamplingMedium
from basin3d.synthesis.serializers import RegionSerializer, SiteSerializer, \
    MeasurementTimeseriesTVPObservationSerializer


class Basin3DSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')
        self.observed_property_var = ObservedPropertyVariable(
            id="ACT", full_name="Acetate (CH3COO)",
            categories="Hydrology,Subsurface")
        self.sampling_medium = SamplingMedium(name="water")

    def test_observed_property_serializer(self):
        """ Test Observed Property Serialization"""

        obj = ObservedProperty(description="Acetate (CH3COO)",
                               observed_property_variable=self.observed_property_var,
                               sampling_medium=self.sampling_medium,
                               datasource=self.datasource)

        # important if the serializer uses any query_params this won't work
        #   b/c the django test request does not return a django request
        s = ObservedPropertySerializer(obj, context={'request': None})

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"url": None,
                          "sampling_medium": "water",
                          "datasource": "Alpha",
                          "observed_property_variable": "ACT",
                          "description": "Acetate (CH3COO)"})



class SynthesisSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name='Alpha')

    def test_region_serializer(self):
        """ Test Region Serialization"""

        obj = models.field.Region(self.datasource, name="a region",
                                  id="SI123", description="US", geom={})

        s = RegionSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"id": "A-SI123", "description": "US", "geom": {}, 'name': 'a region',
                          "url": None})

    def test_site_serializer(self):
        """ Test Site Serialization"""

        obj = models.field.Site(self.datasource, id=1, name="Foo",
                                description="Foo Bar Site",
                                country="US",
                                state_province="California",
                                utc_offset=-6,
                                center_coordinates=models.field.GeographicCoordinate(
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

    def test_measurement_timeseries_tvp_observation_serializer(self):
        """ Test MeasurementTimeseriesTVPObservation Serializer """

        obj = models.measurement.MeasurementTimeseriesTVPObservation(
            self.datasource,
            id="timeseries01",
            utc_offset="9",
            phenomenon_time="2018-11-07T15:28:20",
            result_quality=models.measurement.ResultQuality.RESULT_QUALITY_CHECKED,
            geographical_group_id=1,
            geographical_group_type=GeographicalGroup.POINT_LOCATION,
            aggregation_duration="daily",
            time_reference_position="start",
            observed_property_variable="Acetate",
            statistic="mean",
            result_points=[models.measurement.TimeValuePair("2018-11-07T15:28:20", "5.32")],
            unit_of_measurement="m"
        )

        s = MeasurementTimeseriesTVPObservationSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {
                             "id": "A-timeseries01",
                             "type": "measurement_tvp_timeseries",
                             "utc_offset": 9,
                             "phenomenon_time": "2018-11-07T15:28:20",
                             "result_quality": "checked",
                             "geographical_group_id": "A-1",
                             "geographical_group_type": "pointlocation",
                             "aggregation_duration": "daily",
                             "time_reference_position": "start",
                             "observed_property": 1,
                             "statistic": "mean",
                             "result_points": [["2018-11-07T15:28:20", "5.32"]],
                             "unit_of_measurement": "m"
                         })
