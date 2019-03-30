from basin3d.synthesis.models import Person

import json

from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from basin3d.synthesis import models
from basin3d.serializers import ObservedPropertySerializer
from basin3d.models import DataSource, GeographicalGroup, ObservedProperty, \
    ObservedPropertyVariable, SamplingMedium, FeatureTypes, SpatialSamplingShapes
from basin3d.synthesis.serializers import MonitoringFeatureSerializer, \
    RegionSerializer, SiteSerializer, \
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

    def test_monitoring_serializer(self):
        """ Test Monitoring Serializer """

        obj = models.field.MonitoringFeature(
            datasource=self.datasource,
            id="Region1",
            name="AwesomeRegion",
            description="This region is really awesome.",
            type=FeatureTypes.REGION,
            shape=SpatialSamplingShapes.SHAPE_SURFACE,
            coordinates=models.field.Coordinate(representative=models.field.RepresentativeCoordinate(
                representative_point=models.field.AbsoluteCoordinate(
                    horizontal_position=models.field.GeographicCoordinate(
                        units=models.field.GeographicCoordinate.UNITS_DEC_DEGREES,
                        latitude=70.4657, longitude=-20.4567,
                        datum=models.field.GeographicCoordinate.DATUM_NAD83),
                    vertical_extent=models.field.AltitudeCoordinate(
                        datum=models.field.AltitudeCoordinate.DATUM_NAVD88,
                        value=1500,
                        distance_units=models.field.VerticalCoordinate.DISTANCE_UNITS_FEET)),
                representative_point_type=models.field.RepresentativeCoordinate.REPRESENTATIVE_POINT_TYPE_CENTER_LOCAL_SURFACE)
            )
        )

        s = MonitoringFeatureSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(
            json.loads(json_obj.decode('utf-8')),
            {"id": "A-Region1", "name": "AwesomeRegion",
             "description": "This region is really awesome.",
             "type": "Region", "shape": "Surface",
             "coordinates": {
                 "absolute": None,
                 "representative": {
                     "representative_point": {
                         "horizontal_position": [{
                             "units": "DD", "latitude": 70.4657, "longitude": -20.4567,
                             "datum": "NAD83", "type": "geographic"
                         }],
                         "vertical_extent": [{
                            "datum": "NAVD88", "value": 1500.0, "distance_units": "feet",
                             "resolution": None, "type": "altitude"
                         }]
                     },
                     "representative_point_type": "Center Local Surface",
                     "vertical_position": None
                 }
             },
             "description_reference": None,
             "related_party": [],
             "related_sampling_feature_complex": [],
             "url": None,
             "utc_offset": None,
             "observed_property_variables": None
             }
        )

        obj = models.field.MonitoringFeature(
            datasource=self.datasource,
            id="1",
            name="Point Location 1",
            description="The first point.",
            type=FeatureTypes.POINT,
            shape=SpatialSamplingShapes.SHAPE_POINT,
            coordinates=models.field.Coordinate(
                absolute=models.field.AbsoluteCoordinate(
                    horizontal_position=models.field.GeographicCoordinate(
                        units=models.field.GeographicCoordinate.UNITS_DEC_DEGREES,
                        latitude=70.4657, longitude=-20.4567,
                        datum=models.field.GeographicCoordinate.DATUM_NAD83),
                    vertical_extent=models.field.AltitudeCoordinate(
                        datum=models.field.AltitudeCoordinate.DATUM_NAVD88,
                        value=1500,
                        distance_units=models.field.VerticalCoordinate.DISTANCE_UNITS_FEET)),
                representative=models.field.RepresentativeCoordinate(
                    vertical_position=models.field.DepthCoordinate(
                        datum=models.field.DepthCoordinate.DATUM_LOCAL_SURFACE,
                        value=-0.5,
                        distance_units=models.field.VerticalCoordinate.DISTANCE_UNITS_METERS)
                )
            ),
            observed_property_variables=["Ag", "Acetate"],
            related_sampling_feature_complex=[
                models.field.RelatedSamplingFeature(datasource=self.datasource,
                                                    related_sampling_feature="Region1",
                                                    related_sampling_feature_type=FeatureTypes.REGION,
                                                    role=models.field.RelatedSamplingFeature.ROLE_PARENT)]
        )

        s = MonitoringFeatureSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(
            json.loads(json_obj.decode('utf-8')),
            {"id": "A-1", "name": "Point Location 1",
             "description": "The first point.",
             "type": "Point", "shape": "Point",
             "coordinates": {
                 "absolute": {
                     "horizontal_position": [{
                         "units": "DD", "latitude": 70.4657,
                         "longitude": -20.4567, "datum": "NAD83", "type": "geographic"
                     }],
                     "vertical_extent": [{
                         "datum": "NAVD88", "value": 1500.0,
                         "distance_units": "feet", "resolution": None, "type": "altitude"
                     }]
                 },
                 "representative": {
                     "representative_point_type": None, "representative_point": None,
                     "vertical_position": {
                          "datum": "LS", "value": -0.5, "distance_units": "meters",
                          "type": "depth", "resolution": None
                     }
                 }
             },
             "description_reference": None,
             "observed_property_variables": ["ACT", "Ag"],
             "related_party": [],
             "url": None,
             "utc_offset": None,
             "related_sampling_feature_complex": [{"related_sampling_feature": "A-Region1",
                                                   "related_sampling_feature_type": "Region",
                                                   "role": "Parent", "url": None}]
             }
        )

    # delete
    def test_region_serializer(self):
        """ Test Region Serialization"""

        obj = models.field.Region(self.datasource, name="a region",
                                  id="SI123", description="US", geom={})

        s = RegionSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(json.loads(json_obj.decode('utf-8')),
                         {"id": "A-SI123", "description": "US", "geom": {}, 'name': 'a region',
                          "url": None})

    # delete
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
            feature_of_interest=1,
            feature_of_interest_type=FeatureTypes.POINT,
            # geographical_group_id=1,
            # geographical_group_type=GeographicalGroup.POINT_LOCATION,
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
                             "feature_of_interest": "A-1",
                             "feature_of_interest_type": "Point",
                             "aggregation_duration": "daily",
                             "time_reference_position": "start",
                             "observed_property": 1,
                             "statistic": "mean",
                             "result_points": [["2018-11-07T15:28:20", "5.32"]],
                             "unit_of_measurement": "m"
                         })
