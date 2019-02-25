

from django.test import TestCase
from basin3d.models import DataSource, GeographicalGroup
from basin3d.synthesis.models.field import Region
from basin3d.synthesis.models.measurement import Observation, \
    MeasurementTimeseriesTVPObservation, ResultQuality, TimeValuePair


class ModelTests(TestCase):
    def setUp(self):
        self.datasource = DataSource.objects.get(name="Alpha")

    def test_region_create(self):
        """ Test Region Creation"""

        a_region = Region(self.datasource, name="a site",
                          id="SI123",
                          description="This is for my site description", )

        self.assertEqual("a site", a_region.name)
        self.assertEqual("A-SI123", a_region.id)
        self.assertEqual("This is for my site description", a_region.description)

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
            geographical_group_id="Point011",
            geographical_group_type=GeographicalGroup.POINT_LOCATION)

        assert obs01.datasource.name == "Alpha"
        assert obs01.id == "A-timeseries01"
        assert obs01.utc_offset == "9"
        assert obs01.phenomenon_time == "20180201"
        assert obs01.observed_property is None
        assert obs01.result_quality == ResultQuality().RESULT_QUALITY_CHECKED
        assert obs01.geographical_group_id == "A-Point011"
        assert obs01.geographical_group_type == GeographicalGroup.POINT_LOCATION

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
            geographical_group_id="Point011",
            geographical_group_type=GeographicalGroup.POINT_LOCATION,
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
        assert obs01.geographical_group_id == "A-Point011"
        assert obs01.geographical_group_type == GeographicalGroup.POINT_LOCATION
        assert obs01.aggregation_duration == "daily"
        assert obs01.time_reference_position == "start"
        assert obs01.statistic == "mean"
        assert obs01.unit_of_measurement == "m"
