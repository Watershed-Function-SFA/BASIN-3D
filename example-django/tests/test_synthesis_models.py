

from django.test import TestCase
from basin3d.models import DataSource, FeatureTypes, SpatialSamplingShapes
from basin3d.synthesis.models.field import MonitoringFeature, Coordinate, \
    AbsoluteCoordinate, RepresentativeCoordinate, GeographicCoordinate, AltitudeCoordinate, \
    DepthCoordinate, VerticalCoordinate, RelatedSamplingFeature
from basin3d.synthesis.models.measurement import Observation, \
    MeasurementTimeseriesTVPObservation, ResultQuality, TimeValuePair


class ModelTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name="Alpha")

    def test_monitoring_feature_create(self):
        """
        Test instance of monitoring feature
        :return: n/a
        """

        a_region = MonitoringFeature(
            datasource=self.datasource,
            id="Region1",
            name="AwesomeRegion",
            description="This region is really awesome.",
            feature_type=FeatureTypes.REGION,
            shape=SpatialSamplingShapes.SHAPE_SURFACE,
            coordinates=Coordinate(representative=RepresentativeCoordinate(
                representative_point=AbsoluteCoordinate(
                    horizontal_position=GeographicCoordinate(
                        units=GeographicCoordinate.UNITS_DEC_DEGREES,
                        latitude=70.4657, longitude=-20.4567),
                    vertical_extent=AltitudeCoordinate(
                        datum=AltitudeCoordinate.DATUM_NAVD88,
                        value=1500, distance_units=VerticalCoordinate.DISTANCE_UNITS_FEET)),
                representative_point_type=RepresentativeCoordinate.REPRESENTATIVE_POINT_TYPE_CENTER_LOCAL_SURFACE)
            )
        )

        assert a_region.datasource.name == "Alpha"
        assert a_region.id == "A-Region1"
        assert a_region.name == "AwesomeRegion"
        assert a_region.feature_type == FeatureTypes.REGION
        assert a_region.description == "This region is really awesome."
        assert a_region.shape == SpatialSamplingShapes.SHAPE_SURFACE
        assert a_region.coordinates.representative.representative_point.horizontal_position[0].units == \
            GeographicCoordinate.UNITS_DEC_DEGREES
        assert a_region.coordinates.representative.representative_point.horizontal_position[0].latitude == 70.4657
        assert a_region.coordinates.representative.representative_point.horizontal_position[0].longitude == -20.4567
        assert a_region.coordinates.representative.representative_point.vertical_extent[0].datum == \
            AltitudeCoordinate.DATUM_NAVD88
        assert a_region.coordinates.representative.representative_point.vertical_extent[0].value == 1500
        assert a_region.coordinates.representative.representative_point.vertical_extent[0].distance_units == \
            VerticalCoordinate.DISTANCE_UNITS_FEET
        assert a_region.coordinates.representative.representative_point_type == \
               RepresentativeCoordinate.REPRESENTATIVE_POINT_TYPE_CENTER_LOCAL_SURFACE

        a_point = MonitoringFeature(
            datasource=self.datasource,
            id="1",
            name="Point Location 1",
            description="The first point.",
            feature_type=FeatureTypes.POINT,
            shape=SpatialSamplingShapes.SHAPE_POINT,
            coordinates=Coordinate(
                absolute=AbsoluteCoordinate(
                    horizontal_position=GeographicCoordinate(
                        units=GeographicCoordinate.UNITS_DEC_DEGREES,
                        latitude=70.4657, longitude=-20.4567),
                    vertical_extent=AltitudeCoordinate(
                        datum=AltitudeCoordinate.DATUM_NAVD88,
                        value=1500,
                        distance_units=VerticalCoordinate.DISTANCE_UNITS_FEET)),
                representative=RepresentativeCoordinate(
                    vertical_position=DepthCoordinate(
                        datum=DepthCoordinate.DATUM_LOCAL_SURFACE,
                        value=-0.5, distance_units=VerticalCoordinate.DISTANCE_UNITS_METERS)
                )
            ),
            observed_property_variables=["Ag", "Acetate"],
            related_sampling_feature_complex=[
                RelatedSamplingFeature(datasource=self.datasource,
                                       related_sampling_feature="Region1",
                                       related_sampling_feature_type=FeatureTypes.REGION,
                                       role=RelatedSamplingFeature.ROLE_PARENT)]
        )

        assert a_point.datasource.name == "Alpha"
        assert a_point.id == "A-1"
        assert a_point.name == "Point Location 1"
        assert a_point.feature_type == FeatureTypes.POINT
        assert a_point.description == "The first point."
        assert a_point.shape == SpatialSamplingShapes.SHAPE_POINT
        assert a_point.coordinates.absolute.horizontal_position[0].units == \
            GeographicCoordinate.UNITS_DEC_DEGREES
        assert a_point.coordinates.absolute.horizontal_position[0].latitude == 70.4657
        assert a_point.coordinates.absolute.horizontal_position[0].longitude == -20.4567
        assert a_point.coordinates.absolute.vertical_extent[0].datum == \
            AltitudeCoordinate.DATUM_NAVD88
        assert a_point.coordinates.absolute.vertical_extent[0].value == 1500
        assert a_point.coordinates.absolute.vertical_extent[0].distance_units == \
            VerticalCoordinate.DISTANCE_UNITS_FEET
        assert a_point.coordinates.representative.vertical_position.value == -0.5
        assert a_point.coordinates.representative.vertical_position.distance_units == \
            VerticalCoordinate.DISTANCE_UNITS_METERS
        assert a_point.coordinates.representative.vertical_position.datum == \
            DepthCoordinate.DATUM_LOCAL_SURFACE
        assert a_point.observed_property_variables == ["ACT", "Ag"]
        assert a_point.related_sampling_feature_complex[0].related_sampling_feature == "A-Region1"
        assert a_point.related_sampling_feature_complex[0].role == "PARENT"

    def test_observation_create(self):
        """
        Test instance of observation model class
        NOTE: In practice, the Observation should not be used stand alone
        :return: n/a
        """
        obs01 = Observation(
            datasource=self.datasource,
            id="timeseries01",
            utc_offset="9",
            phenomenon_time="20180201",
            result_quality=ResultQuality().RESULT_QUALITY_CHECKED,
            feature_of_interest="Point011")

        assert obs01.datasource.name == "Alpha"
        assert obs01.id == "A-timeseries01"
        assert obs01.utc_offset == "9"
        assert obs01.phenomenon_time == "20180201"
        assert obs01.observed_property is None
        assert obs01.result_quality == ResultQuality().RESULT_QUALITY_CHECKED
        assert obs01.feature_of_interest == "Point011"

    def test_measurement_timeseries_tvp_observation_create(self):
        """
        Test instance of Measurement Timeseries TVP Observation
        :return: n/a
        """
        obs01 = MeasurementTimeseriesTVPObservation(
            datasource=self.datasource,
            id="timeseries01",
            utc_offset="9",
            phenomenon_time="20180201",
            result_quality=ResultQuality().RESULT_QUALITY_CHECKED,
            feature_of_interest="Point011",
            feature_of_interest_type=FeatureTypes.POINT,
            aggregation_duration="daily",
            time_reference_position="start",
            observed_property_variable="Acetate",
            statistic="mean",
            result_points=[TimeValuePair("201802030100", "5.32")],
            unit_of_measurement="m"
        )

        assert obs01.datasource.name == "Alpha"
        assert obs01.id == "A-timeseries01"
        assert obs01.utc_offset == "9"
        assert obs01.phenomenon_time == "20180201"
        assert obs01.observed_property == 1
        assert obs01.observed_property_variable is None
        assert obs01.result_quality == ResultQuality.RESULT_QUALITY_CHECKED
        assert obs01.feature_of_interest == "Point011"
        assert obs01.feature_of_interest_type == FeatureTypes.POINT
        assert obs01.aggregation_duration == "daily"
        assert obs01.time_reference_position == "start"
        assert obs01.statistic == "mean"
        assert obs01.unit_of_measurement == "m"
