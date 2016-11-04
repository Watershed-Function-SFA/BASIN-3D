===================
BASIN-3D Quickstart
===================

BASIN-3d is a  Django app that acts as a  Broker for Assimilation, Synthesis and Integration of eNvironmental
Diverse, Distributed Datasets.

Detailed documentation is in the "docs" directory.

Django Settings
---------------

Add "basin3d" and its dependencies to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django_extensions',
        'rest_framework',
        'djangoplugins',
        'basin3d'
    ]


URLConf
-------

Include the basin3d URLconf in your project urls.py like this::

    url(r'^', include('basin3d.urls')),

Implement Data Source plugins
-----------------------------

Create one or more plugins in a plugins module in `your-app/plugins.py`.

Add the apps broker measurement variables in a multi-dimensional array::

    # Format: id, full_name, categories (ordered by priority)
    MEASUREMENT_VARIABLES = [["ACT", "Acetate (CH3COO)", ["Geochemistry", "Anions"]],
                            ["Ag", "Silver (Ag)", ["Geochemistry", "Trace elements"]],
                            ["Al", "Aluminum (Al)", ["Geochemistry", "Trace elements"]],
                            ["As", "Arsenic (As)", ["Geochemistry", "Trace elements"]],
                            ]

Extend the broker source plugin with the described attributes::

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


Create view classes for the desired synthesis models::

    class AlphaRegionView(with_metaclass(DataSourcePluginViewMeta)):

        synthesis_model_class=Region

        def list(self, request):
            """
            Generate the Regsion for the Alpha DataSource Plugin
            :param request: the current http request
            """
            pass

        def get(self,request, pk=None):
            """
            Get an Alpha DataSource Plugin Region
            :param request: the current http request
            :param pk: primary key
            """
            pass


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