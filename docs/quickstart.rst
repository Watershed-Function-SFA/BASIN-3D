===================
BASIN-3D Quickstart
===================

BASIN-3D is a  Django app that acts as a  Broker for Assimilation, Synthesis and Integration of eNvironmental
Diverse, Distributed Datasets.

Detailed documentation is in the "docs" directory.

Django Settings
---------------

Add "basin3d" and its dependencies to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        <yourapp>,
        'djangoplugins',
        'basin3d',
        'django_extensions',
        'rest_framework',
    ]


URLConf
-------

Include the basin3d URLconf in your project urls.py like this::

    url(r'^', include('basin3d.urls')),

Implement Data Source plugins
-----------------------------

Create one or more plugins in a plugins module in `your-app/plugins.py`.

Add the apps broker measurement variables in a multi-dimensional array::

    # Format: (id, full_name, (categories ordered by priority) )
    MEASUREMENT_VARIABLES = [["ACT", "Acetate (CH3COO)", ["Geochemistry", "Anions"]],
                            ["Ag", "Silver (Ag)", ["Geochemistry", "Trace elements"]],
                            ["Al", "Aluminum (Al)", ["Geochemistry", "Trace elements"]],
                            ["As", "Arsenic (As)", ["Geochemistry", "Trace elements"]],
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
Extend the broker source plugin with the described attributes::

    class AlphaSourcePlugin(DataSourcePluginPoint):

        name = 'alpha-source-plugin'
        title = 'Alpha Source Plugin'
        plugin_view_classes = (AlphaRegionView, AlphaModelView, AlphaModelDomainView,AlphaMeshView)

        class DataSourceMeta:
            # Data Source attributes
            location = 'https://asource.foo'
            id = 'Alpha'  # unique id for the datasource
            id_prefix = 'A' # id prefix to make model object ids unique across datasources
            name = id  # Human Friendly Data Source Name
            credentials_format = 'username:\npassword:\n'

            # format basin id:measurement variable id
            measure_variable_map = OrderedDict(
                [('ACT', 'Acetate'), ('Ag', 'Ag'), ('Al', 'Al'), ('As', 'As')])


Create view classes for the desired synthesis models::

    class AlphaModelView(with_metaclass(DataSourcePluginViewMeta)):
        synthesis_model_class = Model

        def list(self, request):
            """
            Generate the simulations.Models for this datasource
            """

            # NOTE: Replace this with a call to the data source
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

            # NOTE: Replace this with a call to the data source
            for s in self.list(request):
                if s.id.endswith(pk):
                    return s
            return None

Create a  Keyset
----------------
Credentials for data source are stored in an encrypted database field.  The keyset used to encrypt the field
must be created with python-keyczar. Python-keyczar is a dependency of BASIN-3D and should have been installed
with the BASIN-3D framework::

    $ pip install python-keyczar
    $ mkdir .keyset
    $ keyczart create --location=.keyset --purpose=crypt --name=basin3d
    $ keyczart addkey --location=.keyset --status=primary

The default settings look for .keyset in the BASE directory of your applications.  If you would like to change it,
do the following in your settings.py::

    ENCRYPTED_FIELD_KEYS_DIR = <path to the keyset directory>

Migrate the App
---------------

Run `python manage.py migrate` to create the BASIN-3d models. This will create the database and load the app's
plugins.

Setup Credentials
-----------------

Setup credentials for your data sources with `manage.py`

Display credentials format for a Broker Source pluging]::

    $ bin/python manage.py credentialsformat Alpha
    username:
    password:

Show the current credentials for a Broker source plugin::

     $ bin/python manage.py showcredentials Alpha

Upload new credentials from standard input::

    $ bin/python manage.py uploadcredentials Alpha < credentials.txt

OR::

    $ bin/python manage.py uploadcredentials Alpha
    username: foo
    password: barsecrent
    <Ctr D> to Exit


Run the Server
--------------

Start the development server and visit http://127.0.0.1:8000/admin/
to manage a BASIN-3D models (you'll need the Admin app enabled).::

    url(r'^admin/', include(admin.site.urls))  # admin site


Visit http://127.0.0.1:8000/v1 to to view the REST api.