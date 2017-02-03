import logging
from collections import OrderedDict

from basin3d.plugins import DataSourcePluginPoint, DataSourcePluginViewMeta
from basin3d.synthesis.models import simulations
from basin3d.synthesis.models.field import Region
from basin3d.synthesis.models.simulations import Model, ModelDomain, Mesh
from django.utils.six import with_metaclass
from rest_framework import status

logger = logging.getLogger(__name__)

# Format: id, full_name, categories (ordered by priority)
MEASUREMENT_VARIABLES = [["ACT", "Acetate (CH3COO)", ["Geochemistry", "Anions"]],
                         ["Ag", "Silver (Ag)", ["Geochemistry", "Trace elements"]],
                         ["Al", "Aluminum (Al)", ["Geochemistry", "Trace elements"]],
                         ["As", "Arsenic (As)", ["Geochemistry", "Trace elements"]],
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


class AlphaSourcePlugin(DataSourcePluginPoint):

    name = 'alpha-source-plugin'
    title = 'Alpha Source Plugin'
    plugin_view_classes =  (AlphaRegionView, AlphaModelView, AlphaModelDomainView, AlphaMeshView)

    def direct(self, request, direct_path):
        """
        Handle direct calls the the JAEA Geo API

        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        # Return content and status
        return type('Dummy', (object,), {
                    "content": '{"message":"This is a direct call to the datasource", "url":"https://asource.foo/'
                               +direct_path+
                               '"}',
                    "status":status.HTTP_200_OK })

    class DataSourceMeta:
        # Data Source attributes
        location = 'https://asource.foo/'
        id = 'Alpha'  # unique id for the datasource
        id_prefix = 'A'
        name = id  # Human Friendly Data Source Name
        credentials_format = 'username:\npassword:\n'

        # format basin id:measurement variable id
        measure_variable_map = OrderedDict(
            [('ACT', 'Acetate'), ('Ag', 'Ag'), ('Al', 'Al'), ('As', 'As')])
