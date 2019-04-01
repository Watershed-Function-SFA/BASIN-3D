import logging

from basin3d.models import GeographicalGroup, FeatureTypes, SpatialSamplingShapes
from basin3d.plugins import DataSourcePluginPoint, DataSourcePluginViewMeta
from basin3d.synthesis.models import measurement, Person
from basin3d.synthesis.models.field import Region, Site, Plot, PointLocation, MeasurementPosition, \
    GeographicCoordinate, DepthCoordinate, MonitoringFeature, AltitudeCoordinate, \
    Coordinate, RepresentativeCoordinate, AbsoluteCoordinate, VerticalCoordinate, \
    RelatedSamplingFeature
from basin3d.synthesis.models.measurement import MeasurementTimeseriesTVPObservation
from django.utils.six import with_metaclass

logger = logging.getLogger(__name__)


class AlphaMonitoringFeatureView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = MonitoringFeature

    def list(self, request, **kwargs):
        """
        Get Monitoring Feature Info
        """

        obj_region = self.synthesis_model_class(
            datasource=self.datasource,
            id="Region1",
            name="AwesomeRegion",
            description="This region is really awesome.",
            type=FeatureTypes.REGION,
            shape=SpatialSamplingShapes.SHAPE_SURFACE,
            coordinates=Coordinate(representative=RepresentativeCoordinate(
                representative_point=AbsoluteCoordinate(
                    horizontal_position=GeographicCoordinate(
                        units=GeographicCoordinate.UNITS_DEC_DEGREES,
                        latitude=70.4657, longitude=-20.4567),
                    vertical_extent=AltitudeCoordinate(
                        datum=AltitudeCoordinate.DATUM_NAVD88,
                        value=1500,
                        distance_units=VerticalCoordinate.DISTANCE_UNITS_FEET)),
                representative_point_type=RepresentativeCoordinate.REPRESENTATIVE_POINT_TYPE_CENTER_LOCAL_SURFACE)
            )
        )

        yield obj_region

        obj_point = self.synthesis_model_class(
            datasource=self.datasource,
            id="1",
            name="Point Location 1",
            description="The first point.",
            type=FeatureTypes.POINT,
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
                        value=-0.5,
                        distance_units=VerticalCoordinate.DISTANCE_UNITS_METERS)
                )
            ),
            observed_property_variables=["Ag", "Acetate"],
            related_sampling_feature_complex=[
                RelatedSamplingFeature(datasource=self.datasource,
                                       related_sampling_feature="Region1",
                                       related_sampling_feature_type=FeatureTypes.REGION,
                                       role=RelatedSamplingFeature.ROLE_PARENT)]
        )

        yield obj_point

    def get(self, request, pk=None):
        """
        Get a MonitoringFeature
        :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaSiteView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = Site

    def list(self, request, **kwargs):
        """
        Get the Site information


        """
        obj = self.synthesis_model_class(self.datasource, id=1, name="Foo",
                                         description="Foo Bar Site",
                                         country="US",
                                         state_province="California",
                                         utc_offset=-6,
                                         center_coordinates=GeographicCoordinate(
                                             latitude=90.0,
                                             longitude=90.0,
                                             datum=GeographicCoordinate.DATUM_WGS84,
                                             units=GeographicCoordinate.UNITS_DEC_SECONDS
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

        yield obj

    def get(self, request, pk=None):
        """
        Get a Site
        :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaPlotView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = Plot

    def list(self, request, **kwargs):
        """
        Get the Site information


        """
        obj = self.synthesis_model_class(self.datasource, id=1, name="Plot 1",
                                         site_id="1",
                                         geom={},
                                         pi=Person(first_name="Jessica",
                                                   last_name="Jones",
                                                   email="jjones@foo.bar",
                                                   institution="DC Comics"),
                                         )

        yield obj

    def get(self, request, pk=None):
        """
        Get a Site
        :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaPointLocationView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = PointLocation

    def list(self, request, **kwargs):
        """
        Get the Site information

        """

        for i in range(10):
            obj = self.synthesis_model_class(self.datasource, id=i,
                                             name="Point Location {}".format(i),
                                             site_id="1",
                                             type="well",
                                             geographical_group_id=i,
                                             geographical_group_type=GeographicalGroup.SITE,
                                             horizontal_position=GeographicCoordinate(
                                                 latitude=90.0,
                                                 longitude=90.0,
                                                 datum=GeographicCoordinate.DATUM_WGS84,
                                                 units=GeographicCoordinate.UNITS_DEC_DEGREES
                                             )
                                             )

            yield obj

    def get(self, request, pk=None):
        """
        Get a Site
        :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaRegionView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = Region

    def list(self, request, **kwargs):
        """
        Get the Region information
        """
        region = self.synthesis_model_class(self.datasource, name="a site",
                                            id="SI123",
                                            description="This is for my site description", )

        yield region

    def get(self, request, pk=None):
        """
        Get a Region
        :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaDataMeasurementTimeseriesTVPObservationView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = MeasurementTimeseriesTVPObservation

    def list(self, request, **kwargs):
        """ Generate the MeasurementTimeseriesTVPObservation

          Attributes:
            - *id:* string, Cs137 MR survey ID
            - *observed_property:* string, Cs137MID
            - *utc_offset:* float (offset in hours), +9
            - *geographical_group_id:* string, River system ID (Region ID).
            - *geographical_group_type* enum (sampling_feature, site, plot, region)
            - *results_points:* Array of DataPoint objects

        """
        data = []
        from datetime import date
        for num in range(1, 10):
            data.append((date(2016, 2, num), num * 0.3454))

        for num in range(1, 3):
            yield measurement.MeasurementTimeseriesTVPObservation(
                self.datasource,
                id=num,
                observed_property=1,
                utc_offset=-8-num,
                feature_of_interest=1,
                feature_of_interest_type=FeatureTypes.POINT,
                unit_of_measurement="nm",
                aggregation_duration="daily",
                result_quality="checked",
                time_reference_position=None,
                statistic="mean",
                result_points=data
            )

    def get(self, request, pk=None):
        """
            Get a MeasurementTimeseriesTVPObservation
            :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaSourcePlugin(DataSourcePluginPoint):
    name = 'alpha-source-plugin'
    title = 'Alpha Source Plugin'
    plugin_view_classes = (AlphaRegionView, AlphaSiteView, AlphaPlotView, AlphaPointLocationView, \
                           AlphaDataMeasurementTimeseriesTVPObservationView, AlphaMonitoringFeatureView)
    # Question: should we use the FeatureTypes CV directly?
    feature_types = ['Region', 'Point', 'Tree']

    class DataSourceMeta:
        """
        This is an internal metadata class for defining additional :class:`~basin3d.models.DataSource`
        attributes.

        **Attributes:**
            - *id* - unique id short name
            - *name* - human friendly name (more descriptive)
            - *location* - resource location
            - *id_prefix* - id prefix to make model object ids unique across datasources
            - *credentials_format* - if the data source requires authentication, this is where the
                format of the stored credentials is defined.

        """
        # Data Source attributes
        location = 'https://asource.foo/'
        id = 'Alpha'  # unique id for the datasource
        id_prefix = 'A'
        name = id  # Human Friendly Data Source Name
