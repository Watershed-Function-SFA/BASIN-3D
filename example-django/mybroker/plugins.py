import logging
from collections import OrderedDict

from django.utils.timezone import now

from basin3d.plugins import BrokerSourcePluginPoint
from basin3d.synthesis.models import Site, DataPoint, Location

logger = logging.getLogger(__name__)

# Format: broker_id, name, unit, primary_category, secondary_category
BROKER_MEASUREMENT_VARIABLES = [["ACT", "Acetate (CH3COO)", "mM", "Geochemistry", " Anions"],
                                ["Ag", "Silver (Ag)", "mg/L", "Geochemistry", "Trace elements"],
                                ["Al", "Aluminum (Al)", "mg/L", "Geochemistry", "Trace elements"],
                                ["As", "Arsenic (As)", "mg/L", "Geochemistry", "Trace elements"],
                                ]


class AlphaSourcePlugin(BrokerSourcePluginPoint):
    name = 'alpha-source-plugin'
    title = 'Alpha Source Plugin'
    prefix = 'A-'

    # Data Source attributes
    datasource_location = 'https://asource.foo'
    datasource_id = 'Alpha'  # unique id for the datasource
    datasource_name = datasource_id  # Human Friendly Data Source Name
    datasource_credentials_format = 'username:\npassword:\n'

    # format broker_id:datasource_parameter_name
    datasource_measure_variable_map = OrderedDict(
        [('ACT', 'Acetate'), ('Ag', 'Ag'), ('Al', 'Al'), ('As', 'As')])

    def get_sites(self, datasource):
        """
        Get the Site information
        :param datasource:
        :return:
        """
        site = Site()
        site.site_id = datasource.name
        site.name = "Alpha Data management"
        site.country = "US"
        site.state_province = "California"
        site.urls = [datasource.location]
        site.contact_name = "Luke Cage"
        site.contact_email = "lcage@dcuniverse.foo"
        site.contact_institution = "Power University"

        yield site

    def get_site(self, datasource, pk):
        """
        Get a Site
        :param datasource:
        :param pk:
        :return:
        """
        if datasource.name == pk:
            for s in self.get_sites(datasource):
                return s
        return None

    def get_data_points(self, datasource, locations=None, measure_variables=None):
        """
            Get the Alpha Plugin Dataset
        """
        for num in range(1,101):

            datapoint = DataPoint()
            datapoint.average = "average"
            datapoint.timestamp = now()
            datapoint.unit = "Mg"
            datapoint.type = "Geochemistry"
            datapoint.measure_variable = "As"
            datapoint.site_id = datasource.name
            datapoint.location = "A-{}".format(num % 10)
            datapoint.value = num * 0.324234
            datapoint.depth = 100 / num

            yield datapoint

    def get_locations(self, datasource):
        """
        Get the locations
        :param datasource:
        :return:
        """
        url = datasource.location
        assert AlphaSourcePlugin.datasource_location == url

        for num in range(10):
            location = Location(location_id="{}{}".format(AlphaSourcePlugin.prefix,
                                                          num),
                                site_id=datasource.name,
                                name="FOO",
                                group="BAR",
                                type="Well",
                                geom={"latitude": 33.324234,
                                      "longitude": 55.094809,
                                      "elevation": 544},
                                measure_variables=['Ag', 'Al', 'As'])

            yield location
