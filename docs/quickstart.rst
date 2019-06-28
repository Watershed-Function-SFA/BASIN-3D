===================
BASIN-3D Quickstart
===================

BASIN-3D is a Django app that acts as a Broker for Assimilation, Synthesis and Integration of eNvironmental
Diverse, Distributed Datasets.

Detailed documentation is in the "docs" directory.

Custom plugins are developed for a broker instance. See ~/example-django/ directory containing the app "mybroker"
for a broker instance example.

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

See ~/example-django/mybroker/urls.py for an example.

Implement Data Source plugins
-----------------------------

Create one or more plugins in a plugins module in `your-app/plugins.py`. The following files
must be placed in `your-app/` directory along side `plugins.py`

`measurement_variables.csv`
...........................
Define your broker variables in a comma separated values (csv) file named `measurement_variables.csv`.
This file must be placed this in `your-app/` directory (e.g `your-app/measurement_variables.csv`) .

.. literalinclude:: ../example-django/mybroker/measurement_variables.csv


`mapping_<plugin_name>.csv`
...........................
Map your measurement variables for your plugin variables. The name of the file should be
`mapping_<plugin_name>.csv`. This file must be placed this in `your-app/` directory
(e.g `your-app/mapping_alpha.csv`) .

.. literalinclude:: ../example-django/mybroker/mapping_alpha.csv


Extend the broker source plugin with the described attributes. The following example is from ~example-django/mybroker/plugins.py.

.. literalinclude:: ../example-django/mybroker/plugins.py
   :language: python
   :lines: 164-191


Create view classes for the desired synthesis models in the broker source plugin (e.g., ~example-django/mybroker/plugins.py).

.. literalinclude:: ../example-django/mybroker/plugins.py
   :language: python
   :lines: 15-87

Create a Keyset
----------------
Credentials for data source are stored in an encrypted database field. The keyset used to encrypt the field
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