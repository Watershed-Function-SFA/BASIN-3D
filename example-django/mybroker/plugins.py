import logging
from basin3d.models import SamplingMedium, MeasurementApproach, GeographicalGroup
from basin3d.plugins import DataSourcePluginPoint, DataSourcePluginViewMeta
from basin3d.synthesis.models import measurement
from basin3d.synthesis.models import simulations
from basin3d.synthesis.models.field import Region
from basin3d.synthesis.models.measurement import DataPointGroup, DataPoint
from basin3d.synthesis.models.simulations import Model, ModelDomain, Mesh, ModelRun
from collections import OrderedDict
from django.utils.six import with_metaclass
from rest_framework import status

logger = logging.getLogger(__name__)

# Format: id, full_name, categories (ordered by priority)
MEASUREMENT_VARIABLES = [["ACT", "Acetate (CH3COO)", ["Geochemistry", "Anions"]],
                         ["Ag", "Silver (Ag)", ["Geochemistry", "Trace elements"]],
                         ["Al", "Aluminum (Al)", ["Geochemistry", "Trace elements"]],
                         ["As", "Arsenic (As)", ["Geochemistry", "Trace elements"], ],
                         ]

MEASUREMENTS = [{'description': """The method is based on the sample filtration and dilution ...""",
                 'variable_id': "ACT",
                 'sampling_medium': SamplingMedium.GROUNDWATER,
                 'measurement_approach': MeasurementApproach.MANUAL},
                {'description': """Aqua regia digestion method.""",
                 'variable_id': "Ag",
                 'sampling_medium': SamplingMedium.SOIL_SEDIMENT,
                 'measurement_approach': MeasurementApproach.SENSOR},
                {'description': """Aqua regia digestion method.""",
                 'variable_id': "Al",
                 'sampling_medium': SamplingMedium.SOIL_SEDIMENT,
                 'measurement_approach': MeasurementApproach.SENSOR},
                {'description': """Aqua regia digestion method.""",
                 'variable_id': "As",
                 'sampling_medium': SamplingMedium.SOIL_SEDIMENT,
                 'measurement_approach': MeasurementApproach.SENSOR}
                ]


class AlphaMeshView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = Mesh

    def list(self, request):
        """
        Get the Mesh information
        """
        mesh = self.synthesis_model_class(self.datasource, id="SI123",
                                          geom={})

        yield mesh

    def get(self, request, pk=None):
        """
        Get a Region
        :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaRegionView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = Region

    def list(self, request):
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


class AlphaModelView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = Model

    def list(self, request):
        """
        Generate the simulations.Models for this datasource
        """
        for num in range(3):
            yield simulations.Model(self.datasource, id="M{}".format(num),
                                    version="1.0",
                                    dimensionality=("1D", "2D", "3D")[num],
                                    url="/testserver/url/{}".format(num))

    def get(self, request, pk=None):
        """
        Get a simulations.Model
        :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaModelRunView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = ModelRun

    def list(self, request):
        """
        Generate the simulations.ModelRuns for this datasource


        """
        for num in range(3):
            yield simulations.ModelRun(self.datasource, id="MR{}".format(num),
                                       name="foo",
                                       start_time=None,
                                       end_time=None,
                                       simulation_length=(num * 10),
                                       simulation_length_units="years",
                                       url="/testserver/url/{}".format(num))

    def get(self, request, pk=None):
        """
        Get a simulations.Model
        :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaModelDomainView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = ModelDomain

    def list(self, request):
        """ Generate the Model Domains"""
        for num in range(1, 10):
            yield simulations.ModelDomain(self.datasource, id="MD{}".format(num),
                                          name="model domain {}".format(num),
                                          url="/testserver/url/{}".format(num),
                                          geom={})

    def get(self, request, pk=None):
        """
            Get a ModelDomain
            :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaDataPointGroupView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = DataPointGroup

    def list(self, request):
        """ Generate the Data Point Group

          Attributes:
            - *id:* string, Cs137 MR survey ID
            - *measurement_id:* string, Cs137MID
            - *start_time:* datetime,  survey start time (month/year)
            - *end_time:* datetime, units: survey end time (month/year)
            - *utc_offset:* float (offset in hours), +9
            - *geographical_group_id:* string, River system ID (Region ID).
            - *geographical_group_type* enum (sampling_feature, site, plot, model_domain, region): Model_domain (or optionally region)
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
                                             geographical_group_type=GeographicalGroup.MODEL_DOMAIN)

    def get(self, request, pk=None):
        """
            Get a ModelDomain
            :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaDataPointView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = DataPoint

    def list(self, request):
        """ Generate the Data Point

        Attributes:
            - *id:* string,
            - *measurement_id:* string,
            - *geographical_group_id:* string (sampling feature can be site/plot/measurement location),
            - *geographical_group_type* enum (sampling_feature, site, plot, model_domain, region): Model_domain (or optionally region)
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
                                                  measurement_id=1,
                                                  geographical_group_id=1,
                                                  geographical_group_type=GeographicalGroup.MESH,
                                                  timestamp=date(2016, num, 1),
                                                  value=num * .3453453,
                                                  units="nm", temporal_resolution="month",
                                                  reference=None,
                                                  utc_offset=-8, )

    def get(self, request, pk=None):
        """
            Get a ModelDomain
            :param pk: primary key
        """
        for s in self.list(request):
            if s.id.endswith(pk):
                return s
        return None


class AlphaSourcePlugin(DataSourcePluginPoint):
    name = 'alpha-source-plugin'
    title = 'Alpha Source Plugin'
    plugin_view_classes = (AlphaRegionView, AlphaModelView, AlphaModelDomainView,
                           AlphaMeshView, AlphaModelRunView, AlphaDataPointGroupView,
                           AlphaDataPointView)


    class DataSourceMeta:
        # Data Source attributes
        location = 'https://asource.foo/'
        id = 'Alpha'  # unique id for the datasource
        id_prefix = 'A'
        name = id  # Human Friendly Data Source Name

        # format basin id:measurement variable id
        measure_variable_map = OrderedDict(
            [('ACT', 'Acetate'), ('Ag', 'Ag'), ('Al', 'Al'), ('As', 'As')])
