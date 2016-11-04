import logging
from collections import OrderedDict

from basin3d.plugins import DataSourcePluginPoint, DataSourcePluginViewMeta
from basin3d.synthesis.models import Region, simulations
from basin3d.synthesis.models.simulations import Model
from basin3d.tests.test_synthesis_models import ModelDomain
from django.utils.six import with_metaclass

logger = logging.getLogger(__name__)

# Format: id, full_name, categories (ordered by priority)
MEASUREMENT_VARIABLES = [["ACT", "Acetate (CH3COO)", ["Geochemistry", "Anions"]],
                         ["Ag", "Silver (Ag)", ["Geochemistry", "Trace elements"]],
                         ["Al", "Aluminum (Al)", ["Geochemistry", "Trace elements"]],
                         ["As", "Arsenic (As)", ["Geochemistry", "Trace elements"]],
                         ]


class AlphaRegionView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = Region

    def list(self, request):
        """
        Get the Region information
        """
        region = self.synthesis_model_class(name="a site",
                                            id="SI123",
                                            description="This is for my site description", )

        yield region

    def get(self, request, pk=None):
        """
        Get a Region
        :param pk: primary key
        """
        for s in self.list(request):
            if s.id == pk:
                return s
        return None


class AlphaModelView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = Model

    def list(self, request):
        """
        Generate the simulations.Models for this datasource
        """
        for num in range(3):
            yield simulations.Model(id="M{}".format(num),
                                    version="1.0",
                                    dimensionality=("1D", "2D", "3D")[num],
                                    url="/testserver/url/{}".format(num))

    def get(self, request, pk=None):
        """
        Get a simulations.Model
        :param pk: primary key
        """
        for s in self.list(request):
            if s.id == pk:
                return s
        return None


class AlphaModelDomainView(with_metaclass(DataSourcePluginViewMeta)):
    synthesis_model_class = ModelDomain

    def list(self, request):
        """ Generate the Model Domains"""
        for num in range(1, 10):
            yield simulations.ModelDomain(model_domain_id="MD{}".format(num),
                                          model_domain_name="model domain {}".format(num),
                                          url="/testserver/url/{}".format(num),
                                          geom={},
                                          meshes=[simulations.Mesh(mesh_id="1",
                                                                   parameters=[],
                                                                   initial_conditions=[])])

    def get(self, request, pk=None):
        """
            Get a ModelDomain
            :param pk: primary key
        """
        for s in self.list(request):
            if s.model_domain_id == pk:
                return s
        return None


class AlphaSourcePlugin(DataSourcePluginPoint):

    name = 'alpha-source-plugin'
    title = 'Alpha Source Plugin'
    plugin_view_classes = (AlphaRegionView, AlphaModelView, AlphaModelDomainView)

    class DataSourceMeta:
        # Data Source attributes
        location = 'https://asource.foo'
        id = 'Alpha'  # unique id for the datasource
        name = id  # Human Friendly Data Source Name
        credentials_format = 'username:\npassword:\n'

        # format basin id:measurement variable id
        measure_variable_map = OrderedDict(
            [('ACT', 'Acetate'), ('Ag', 'Ag'), ('Al', 'Al'), ('As', 'As')])
