import csv
import importlib
import inspect
import os
import sys

from django.apps import AppConfig
from django.conf import settings
from django.db import IntegrityError
from django.db.models.signals import post_migrate


def load_data_sources(sender, **kwargs):
    """
    Load the Broker data sources from the registered plugins.

    :param sender:
    :param kwargs:
    :return:
    """

    # Load all the plugins found in apps
    for django_app in settings.INSTALLED_APPS:

        try:
            importlib.import_module("{}.plugins".format(django_app))
        except ImportError:
            pass

    load_sampling_mediums()

    from basin3d.models import SamplingMedium, \
        ObservedProperty, ObservedPropertyVariable, DataSourceObservedPropertyVariable

    from basin3d.plugins import PluginMount
    from basin3d.models import DataSource
    for plugin in PluginMount.plugins:
        module_name = plugin.__module__
        class_name = plugin.__name__
        print("Loading Plugin = {}.{}".format(module_name, class_name))

        try:
            datasource = DataSource.objects.get(name=plugin.get_meta().id)
        except DataSource.DoesNotExist:
            print("Registering NEW Data Source Plugin '{}.{}'".format(module_name, class_name))
            datasource = DataSource()
            if hasattr(plugin.get_meta(), "connection_class"):
                datasource.credentials = plugin.get_meta().connection_class.get_credentials_format()

        # Update the datasource
        datasource.name = plugin.get_meta().id
        datasource.location = plugin.get_meta().location
        datasource.id_prefix = plugin.get_meta().id_prefix
        datasource.plugin_module = module_name
        datasource.plugin_class = class_name
        datasource.save()
        print("Updated Data Source '{}'".format(plugin.get_meta().id))

        load_observed_property_variables(datasource.get_plugin())

        for variable_mapping in __iterate_observed_property_mapping(datasource.get_plugin()):

            sm = SamplingMedium.objects.get(name=variable_mapping["sampling_medium"])
            v = None
            try:
                v = ObservedPropertyVariable.objects.get(id=variable_mapping['broker_id'])
                op = ObservedProperty.objects.get(observed_property_variable=v, datasource=datasource)
                op.sampling_medium = sm
                op.description = variable_mapping['description']
                op.save()

            except ObservedProperty.DoesNotExist:

                op = ObservedProperty(sampling_medium=sm,
                                      description=variable_mapping["description"],
                                      datasource=datasource,
                                      observed_property_variable=v)
                op.save()
                print("Created Observed Property {} for {}".format(v, datasource))
            except IntegrityError as ie:
                # Its OK that is has already been created
                print(str(ie), file=sys.stderr)

            except Exception as e:

                print("Error Registering Measurement '{} {}': {}".format(variable_mapping['broker_id'],
                                                                         variable_mapping['description'], str(e)))
            try:
                datasource_parameter = DataSourceObservedPropertyVariable()
                datasource_parameter.observed_property_variable = v
                datasource_parameter.datasource = datasource
                datasource_parameter.name = variable_mapping['datasource_name']
                datasource_parameter.save()

            except IntegrityError:
                # This object has already been loaded
                pass

            except Exception as e:
                print("Error Registering DataSource Observed Property Variable '{}' for Data Source '{}': {}".
                      format(variable_mapping['broker_id'], datasource.name, str(e)), file=sys.stderr)


def load_observed_property_variables(plugin):
    """
        Load all measurement objects into the database

        :param sender:
        :param kwargs:
        :return:
    """
    from basin3d.models import ObservedPropertyVariable

    plugin_file_path = os.path.dirname(inspect.getfile(plugin.__class__))
    variables_file = os.path.join(plugin_file_path,
                                  "measurement_variables.csv")
    if os.path.exists(plugin_file_path) and os.path.exists(variables_file):

        # Open the CSV from reading
        with open(variables_file, 'r') as csvfile:
            # Create a dictionary reader where the header
            # row becomes the dict keys for each entry.
            reader = csv.DictReader(csvfile)

            # Now iterate over the mapping file and yield
            # each row to the caller
            for row in reader:
                try:
                    # Create a new Measurement Variable
                    p = ObservedPropertyVariable()
                    p.id = row['broker_id']
                    p.full_name = row['description']
                    p.categories = row['categories']
                    p.save()

                except IntegrityError:

                    # This object has already been loaded
                    pass

                except Exception as e:

                    print("Error Registering ObservedPropertyVariable '{}': {}".format(row['broker_id'], str(e)))

    else:
        print("There are no observed property variables to load to load - {} is missing".format(variables_file))


def load_sampling_mediums():
    """
    Load the predefined sampling mediums in the database
    :param sender:
    :param kwargs:
    :return:
    """
    # Load the Sampling Mediums
    from basin3d.models import SamplingMedium
    for sm in SamplingMedium.SAMPLING_MEDIUMS:
        try:
            obj = SamplingMedium(name=sm)
            obj.save()
            print("Created SamplingMedium {}".format(sm))
        except IntegrityError:
            # This object has already been loaded
            pass
        except Exception as e:
            print("Error Registering SamplingMedium '{}': {}".format(sm, str(e)), file=sys.stderr)


def __iterate_observed_property_mapping(plugin):  # ToDo: change this to __iterate_observed_property_mapping
    """
    Generator for iterating over the measurement mapping
    :param plugin: the plugin to find the mapping for
    :yield:  row
    """

    # Grab the file path from the Plugin's python path
    plugin_file_path = os.path.dirname(inspect.getfile(plugin.__class__))
    if os.path.exists(plugin_file_path):

        # There should be a mapping file for this data sources parameters.  If there isn't
        # throw an exception.
        mapping_file = os.path.join(plugin_file_path, "mapping_{}.csv".format(plugin.get_meta().id.lower()))
        if os.path.exists(mapping_file):
            with open(mapping_file, ) as csvfile:
                # Create a dictionary reader where the header
                # row becomes the dict keys for each entry.
                reader = csv.DictReader(csvfile)

                # Now iterate over the mapping file and yield
                # each row to the caller
                for row in reader:
                    yield row
        else:
            raise Exception("There are no measurement variables ({}) mapped for this plugin {}.{}".format(mapping_file,
                                                                                                          plugin.plugin_module,
                                                                                                          plugin.plugin_class))

    else:
        raise Exception("File path does not exist for plugin {}.{}".format(plugin.plugin_module, plugin.plugin_class))


class Basin3DConfig(AppConfig):
    name = 'basin3d'

    def ready(self):
        # Execute the post migration scripts
        post_migrate.connect(load_data_sources, sender=self)
