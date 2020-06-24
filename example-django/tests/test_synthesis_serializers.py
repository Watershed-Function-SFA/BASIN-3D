import json

from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from basin3d.core import models
from basin3d.core.models import MeasurementTimeseriesTVPObservation
from django_basin3d.models import DataSource, FeatureTypes, ObservedProperty, ObservedPropertyVariable, SamplingMedium, \
    SpatialSamplingShapes
from django_basin3d.serializers import ObservedPropertySerializer
from django_basin3d.synthesis.serializers import MeasurementTimeseriesTVPObservationSerializer, \
    MonitoringFeatureSerializer


class Basin3DSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name="Alpha")
        self.plugin_access = self.datasource.get_plugin().get_plugin_access()[MeasurementTimeseriesTVPObservation]
        self.observed_property_var = ObservedPropertyVariable(
            basin3d_id="ACT", full_name="Acetate (CH3COO)",
            categories="Hydrology,Subsurface")
        self.sampling_medium = SamplingMedium(name="WATER")
        self.maxDiff = None

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
                          "sampling_medium": "WATER",
                          "datasource": "Alpha",
                          "observed_property_variable": "ACT",
                          "description": "Acetate (CH3COO)"})


class SynthesisSerializerTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name="Alpha")
        self.plugin_access = self.datasource.get_plugin().get_plugin_access()[MeasurementTimeseriesTVPObservation]

    def test_monitoring_feature_serializer(self):
        """ Test Monitoring Serializer """

        obj = models.MonitoringFeature(
            plugin_access=self.plugin_access,
            id="Region1",
            name="AwesomeRegion",
            description="This region is really awesome.",
            feature_type=FeatureTypes.REGION,
            shape=SpatialSamplingShapes.SHAPE_SURFACE,
            coordinates=models.Coordinate(representative=models.RepresentativeCoordinate(
                representative_point=models.AbsoluteCoordinate(
                    horizontal_position=models.GeographicCoordinate(
                        units=models.GeographicCoordinate.UNITS_DEC_DEGREES,
                        latitude=70.4657, longitude=-20.4567,
                        datum=models.GeographicCoordinate.DATUM_NAD83),
                    vertical_extent=models.AltitudeCoordinate(
                        datum=models.AltitudeCoordinate.DATUM_NAVD88,
                        value=1500,
                        distance_units=models.VerticalCoordinate.DISTANCE_UNITS_FEET)),
                representative_point_type=models.RepresentativeCoordinate.REPRESENTATIVE_POINT_TYPE_CENTER_LOCAL_SURFACE)
            )
        )

        s = MonitoringFeatureSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual(
            json.loads(json_obj.decode('utf-8')),
            {"id": "A-Region1", "name": "AwesomeRegion",
             "description": "This region is really awesome.",
             "feature_type": "REGION", "shape": "SURFACE",
             "coordinates": {
                 "absolute": None,
                 "representative": {
                     "representative_point": {
                         "horizontal_position": [{
                             "units": "DD", "latitude": 70.4657, "longitude": -20.4567,
                             "datum": "NAD83", "type": "GEOGRAPHIC", "y": 70.4657, "x": -20.4567
                         }],
                         "vertical_extent": [{
                             "datum": "NAVD88", "value": 1500.0, "distance_units": "feet",
                             "resolution": None, "type": "ALTITUDE"
                         }]
                     },
                     "representative_point_type": "CENTER LOCAL SURFACE",
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

        obj = models.MonitoringFeature(
            plugin_access=self.plugin_access,
            id="1",
            name="Point Location 1",
            description="The first point.",
            feature_type=FeatureTypes.POINT,
            shape=SpatialSamplingShapes.SHAPE_POINT,
            coordinates=models.Coordinate(
                absolute=models.AbsoluteCoordinate(
                    horizontal_position=models.GeographicCoordinate(
                        units=models.GeographicCoordinate.UNITS_DEC_DEGREES,
                        latitude=70.4657, longitude=-20.4567,
                        datum=models.GeographicCoordinate.DATUM_NAD83),
                    vertical_extent=models.AltitudeCoordinate(
                        datum=models.AltitudeCoordinate.DATUM_NAVD88,
                        value=1500,
                        distance_units=models.VerticalCoordinate.DISTANCE_UNITS_FEET)),
                representative=models.RepresentativeCoordinate(
                    vertical_position=models.DepthCoordinate(
                        datum=models.DepthCoordinate.DATUM_LOCAL_SURFACE,
                        value=-0.5,
                        distance_units=models.VerticalCoordinate.DISTANCE_UNITS_METERS)
                )
            ),
            observed_property_variables=["Ag", "Acetate"],
            related_sampling_feature_complex=[
                models.RelatedSamplingFeature(plugin_access=self.plugin_access,
                                              related_sampling_feature="Region1",
                                              related_sampling_feature_type=FeatureTypes.REGION,
                                              role=models.RelatedSamplingFeature.ROLE_PARENT)]
        )

        s = MonitoringFeatureSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.maxDiff = None
        self.assertEqual(
            json.loads(json_obj.decode('utf-8')),
            {"id": "A-1", "name": "Point Location 1",
             "description": "The first point.",
             "feature_type": "POINT", "shape": "POINT",
             "coordinates": {
                 "absolute": {
                     "horizontal_position": [{
                         "units": "DD", "latitude": 70.4657, "y": 70.4657, "x": -20.4567,
                         "longitude": -20.4567, "datum": "NAD83", "type": "GEOGRAPHIC"
                     }],
                     "vertical_extent": [{
                         "datum": "NAVD88", "value": 1500.0,
                         "distance_units": "feet", "resolution": None, "type": "ALTITUDE"
                     }]
                 },
                 "representative": {
                     "representative_point_type": None, "representative_point": None,
                     "vertical_position": {
                         "datum": "LS", "value": -0.5, "distance_units": "meters",
                         "type": "DEPTH", "resolution": None
                     }
                 }
             },
             "description_reference": None,
             "observed_property_variables": ["ACT", "Ag"],
             "related_party": [],
             "url": None,
             "utc_offset": None,
             "related_sampling_feature_complex": [{"related_sampling_feature": "A-Region1",
                                                   "related_sampling_feature_type": "REGION",
                                                   "role": "PARENT", "url": None}]
             }
        )

    # @pytest.mark.xfail(reason="Serialization problem for ObservedProperty object")
    def test_measurement_timeseries_tvp_observation_serializer(self):
        """ Test MeasurementTimeseriesTVPObservation Serializer """

        obj = models.MeasurementTimeseriesTVPObservation(
            plugin_access=self.plugin_access,
            id="timeseries01",
            utc_offset="9",
            phenomenon_time="2018-11-07T15:28:20",
            result_quality=models.ResultQuality.RESULT_QUALITY_CHECKED,
            feature_of_interest=models.MonitoringFeature(
                plugin_access=self.plugin_access,
                id="1",
                name="Point Location 1",
                description="The first point.",
                feature_type=FeatureTypes.POINT,
                shape=SpatialSamplingShapes.SHAPE_POINT,
                coordinates=models.Coordinate(
                    absolute=models.AbsoluteCoordinate(
                        horizontal_position=models.GeographicCoordinate(
                            units=models.GeographicCoordinate.UNITS_DEC_DEGREES,
                            latitude=70.4657, longitude=-20.4567,
                            datum=models.GeographicCoordinate.DATUM_NAD83),
                        vertical_extent=models.AltitudeCoordinate(
                            datum=models.AltitudeCoordinate.DATUM_NAVD88,
                            value=1500,
                            distance_units=models.VerticalCoordinate.DISTANCE_UNITS_FEET)),
                    representative=models.RepresentativeCoordinate(
                        vertical_position=models.DepthCoordinate(
                            datum=models.DepthCoordinate.DATUM_LOCAL_SURFACE,
                            value=-0.5,
                            distance_units=models.VerticalCoordinate.DISTANCE_UNITS_METERS)
                    )
                ),
                observed_property_variables=["Ag", "Acetate"],
                related_sampling_feature_complex=[
                    models.RelatedSamplingFeature(plugin_access=self.plugin_access,
                                                  related_sampling_feature="Region1",
                                                  related_sampling_feature_type=FeatureTypes.REGION,
                                                  role=models.RelatedSamplingFeature.ROLE_PARENT)]
            ),
            feature_of_interest_type=FeatureTypes.POINT,
            aggregation_duration="DAILY",
            time_reference_position="START",
            observed_property_variable="Acetate",
            statistic="MEAN",
            result_points=[models.TimeValuePair("2018-11-07T15:28:20", "5.32")],
            unit_of_measurement="m"
        )

        s = MeasurementTimeseriesTVPObservationSerializer(obj)

        json_obj = JSONRenderer().render(s.data)
        self.assertEqual({
                             "id": "A-timeseries01",
                             "type": "MEASUREMENT_TVP_TIMESERIES",
                             "utc_offset": 9,
                             "phenomenon_time": "2018-11-07T15:28:20",
                             "result_quality": "CHECKED",
                             "feature_of_interest": {
                                 "id": "A-1", "name": "Point Location 1",
                                 "description": "The first point.",
                                 "feature_type": "POINT", "shape": "POINT",
                                 "coordinates": {
                                     "absolute": {
                                         "horizontal_position": [{
                                             "units": "DD", "latitude": 70.4657, "y": 70.4657, "x": -20.4567,
                                             "longitude": -20.4567, "datum": "NAD83", "type": "GEOGRAPHIC"
                                         }],
                                         "vertical_extent": [{
                                             "datum": "NAVD88", "value": 1500.0,
                                             "distance_units": "feet", "resolution": None, "type": "ALTITUDE"
                                         }]
                                     },
                                     "representative": {
                                         "representative_point_type": None, "representative_point": None,
                                         "vertical_position": {
                                             "datum": "LS", "value": -0.5, "distance_units": "meters",
                                             "type": "DEPTH", "resolution": None
                                         }
                                     }
                                 },
                                 "description_reference": None,
                                 "observed_property_variables": ["ACT", "Ag"],
                                 "related_party": [],
                                 "url": None,
                                 "utc_offset": None,
                                 "related_sampling_feature_complex": [{"related_sampling_feature": "A-Region1",
                                                                       "related_sampling_feature_type": "REGION",
                                                                       "role": "PARENT", "url": None}]
                             },
                             "feature_of_interest_type": "POINT",
                             "aggregation_duration": "DAILY",
                             "time_reference_position": "START",
                             "observed_property_variable": 'ACT',
                             "statistic": "MEAN",
                             "result_points": [["2018-11-07T15:28:20", "5.32"]],
                             "unit_of_measurement": "m"
                         }, json.loads(json_obj.decode('utf-8')))
