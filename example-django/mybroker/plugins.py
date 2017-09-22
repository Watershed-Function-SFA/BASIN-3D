import logging

from basin3d.models import SamplingMedium, MeasurementApproach, GeographicalGroup, Measurement
from basin3d.plugins import DataSourcePluginPoint, DataSourcePluginViewMeta
from basin3d.synthesis.models import measurement, Person
from basin3d.synthesis.models.field import Region, Site, Plot, PointLocation, \
    GeographicCoordinate, MeasurementPosition, DepthCoordinate
from basin3d.synthesis.models.measurement import DataPointGroup, DataPoint
from collections import OrderedDict
from django.utils.six import with_metaclass

logger = logging.getLogger(__name__)

# Format: id, full_name, categories (ordered by priority)
MEASUREMENT_VARIABLES = [["ACT", "Acetate (CH3COO)", ["Geochemistry", "Anions"]],
                         ["Ag", "Silver (Ag)", ["Geochemistry", "Trace elements"]],
                         ["Al", "Aluminum (Al)", ["Geochemistry", "Trace elements"]],
                         ["As", "Arsenic (As)", ["Geochemistry", "Trace elements"], ],
                         ]




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
                                             geographical_group_id=1,
                                             geographical_group_type=GeographicalGroup.PLOT,
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


class AlphaDataPointGroupView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = DataPointGroup

    def list(self, request, **kwargs):
        """ Generate the Data Point Group

          Attributes:
            - *id:* string, Cs137 MR survey ID
            - *measurement_id:* string, Cs137MID
            - *start_time:* datetime,  survey start time (month/year)
            - *end_time:* datetime, units: survey end time (month/year)
            - *utc_offset:* float (offset in hours), +9
            - *geographical_group_id:* string, River system ID (Region ID).
            - *geographical_group_type* enum (sampling_feature, site, plot, region)
            - *results:* Array of DataPoint objects

        """
        for num in range(1, 10):
            from datetime import datetime
            from calendar import monthrange
            last_day = monthrange(2016, num)[-1]
            yield measurement.DataPointGroup(self.datasource, id=num, measurement_id=1,
                                             start_time=datetime(2016, num, 1),
                                             end_time=datetime(2016, num, last_day),
                                             utc_offset=-8,
                                             geographical_group_id=1,
                                             geographical_group_type=GeographicalGroup.SITE)

    def get(self, request, pk=None):
        """
            Get a DataPointGroup
            :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaDataPointView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = DataPoint

    def list(self, request, **kwargs):
        """ Generate the Data Point

        Attributes:
            - *id:* string,
            - *measurement_id:* string,
            - *geographical_group_id:* string (sampling feature can be site/plot/measurement location),
            - *geographical_group_type* enum (sampling_feature, site, plot, region)
            - *unit:* Unit
            - *timestamp: datetime,
            - *value: float,
            - *units: Unit  Cs137UID
            - *resolution: enum(year, month, day, hour, minute, second, millisecond),
            - *reference: string (start, middle, end),
            - *utc_offset: float (offset in hours) - optional
        """
        for num in range(1, 10):
            from datetime import date

            yield measurement.TimeSeriesDataPoint(self.datasource, id=num,
                                                  measurement=Measurement.objects.get(id=1),
                                                  measurement_position=MeasurementPosition(
                                                      self.datasource,
                                                      point_location_id=1,
                                                      vertical_position=DepthCoordinate(
                                                          value=num * .35345,
                                                          distance_units=DepthCoordinate.DISTANCE_UNITS_METERS,
                                                          datum=DepthCoordinate.DATUM_LOCAL_SURFACE)),
                                                  geographical_group_id=1,
                                                  geographical_group_type=GeographicalGroup.POINT_LOCATION,
                                                  timestamp=date(2016, num, 1),
                                                  value=num * .3453453,
                                                  units="nm", temporal_resolution="month",
                                                  reference=None,
                                                  utc_offset=-8, )

    def get(self, request, pk=None):
        """
            Get a DataPoint
            :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaSourcePlugin(DataSourcePluginPoint):
    name = 'alpha-source-plugin'
    title = 'Alpha Source Plugin'
    plugin_view_classes = (AlphaRegionView,
                           AlphaDataPointGroupView,
                           AlphaDataPointView, AlphaSiteView, AlphaPlotView,
                           AlphaPointLocationView)

    class DataSourceMeta:
        # Data Source attributes
        location = 'https://asource.foo/'
        id = 'Alpha'  # unique id for the datasource
        id_prefix = 'A'
        name = id  # Human Friendly Data Source Name

        # format basin id:measurement variable id
        MEASURE_VARIABLE_MAP = OrderedDict(
            [('ACT', 'Acetate'), ('Ag', 'Ag'), ('Al', 'Al'), ('As', 'As')])

        MEASUREMENTS = [
            {'description': """The method is based on the sample filtration and dilution ...""",
             'variable_id': "ACT",
             'sampling_medium': SamplingMedium.GROUNDWATER,
             'approach': MeasurementApproach.MANUAL},
            {'description': """Aqua regia digestion method.""",
             'variable_id': "Ag",
             'sampling_medium': SamplingMedium.SOIL_SEDIMENT,
             'approach': MeasurementApproach.SENSOR},
            {'description': """Aqua regia digestion method.""",
             'variable_id': "Al",
             'sampling_medium': SamplingMedium.SOIL_SEDIMENT,
             'approach': MeasurementApproach.SENSOR},
            {'description': """Aqua regia digestion method.""",
             'variable_id': "As",
             'sampling_medium': SamplingMedium.SOIL_SEDIMENT,
             'approach': MeasurementApproach.SENSOR}
        ]
