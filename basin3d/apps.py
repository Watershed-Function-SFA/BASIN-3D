import importlib

import sys, os, csv, inspect

from django.apps import AppConfig
from django.db import IntegrityError
from django.db.models.signals import post_migrate


def load_data_sources(sender, **kwargs):
    """
    Load the Broker data sources from the registered plugins.

    :param sender:
    :param kwargs:
    :return:
    """

    from djangoplugins.models import Plugin
    from basin3d.models import DataSource
    from basin3d.models import SamplingMedium, Measurement, MeasurementVariable
    SamplingMedium.objects.all().delete()

    for plugin_model in Plugin.objects.all():
        plugin = plugin_model.get_plugin()

        try:
            datasource = DataSource.objects.get(name=plugin.get_meta().id)
        except DataSource.DoesNotExist:
            print("Registering NEW Data Source '{}'".format(plugin.get_meta().id))
            datasource = DataSource()
            if hasattr(plugin.get_meta(), "connection_class"):
                datasource.credentials = plugin.get_meta().connection_class.get_credentials_format()

        # Update the datasource
        datasource.name = plugin.get_meta().id
        datasource.location = plugin.get_meta().location
        datasource.id_prefix = plugin.get_meta().id_prefix
        datasource.plugin = plugin_model
        datasource.save()
        print("Updated Data Source '{}'".format(plugin.get_meta().id))

        for variable_mapping in __iterate_measurement_mapping(plugin):

                try:
                    sm = SamplingMedium.objects.get(name=variable_mapping["sampling_medium"])
                except SamplingMedium.DoesNotExist:
                    sm = SamplingMedium(name=variable_mapping["sampling_medium"])
                    sm.save()




                try:
                    v = MeasurementVariable.objects.get(id=variable_mapping['broker_id'])
                    m = Measurement.objects.get(variable=v, datasource=datasource)
                    m.sampling_medium = sm
                    m.description = variable_mapping['description']
                    m.save()
                except Measurement.DoesNotExist:

                    m = Measurement(sampling_medium=sm,
                                    description=variable_mapping["description"],
                                    datasource=datasource,
                                    variable=v)
                    m.save()
                except IntegrityError:
                    # Its OK that is has already been created
                    pass

                except Exception as e:

                    print("Error Registering Measurement '{} {}': {}".format(variable_mapping['broker_id'], variable_mapping['description'], str(e)))


def load_measurment_objects(sender, **kwargs):
    """
        Load all measurement objects into the database

        Global:

            + Sampling Medium
            + Measurement Approaches

        Plugin Specified

            + MEASURMENT_VARIABLES
             + MEASUREMENTS

        :param sender:
        :param kwargs:
        :return:
    """
    from djangoplugins.models import Plugin
    from basin3d.models import MeasurementVariable, SamplingMedium

    # Load the Sampling Mediums
    for sm in SamplingMedium.SAMPLING_MEDIUMS:
        try:
            obj = SamplingMedium(name=sm)
            obj.save()
        except IntegrityError:
            # This object has already been loaded
            pass
        except Exception as e:
            print("Error Registering SamplingMedium '{}': {}".format(obj.name, str(e)), file=sys.stderr)

    plugins = Plugin.objects.all()
    MeasurementVariable.objects.all().delete()
    for plugin in plugins:
        plugin_path = plugin.pythonpath
        idx = plugin_path.index('plugins')
        module_name = plugin_path[0:idx+len('plugins')]
        app_plugins = importlib.import_module(module_name)

        # Find the directory where the plugs live.
        #  There should be a CSV file with this broker's m
        #  measurement variables in it.
        plugin_file_path = os.path.dirname(inspect.getfile(app_plugins))
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
                        p = MeasurementVariable()
                        p.id = row['broker_id']
                        p.full_name = row['description']
                        p.categories = row['categories']
                        p.save()

                    except IntegrityError:

                        # This object has already been loaded
                        pass

                    except Exception as e:

                        print("Error Registering MeasurementVariable '{}': {}".format(row['broker_id'], str(e)))

                # If Measurement Variables were loaded quit out of the loop
                break
        else:
            print("There are no measurement variables to load to load - {} is missing".format(variables_file))


def load_datasource_parameters(sender,**kwargs):
    """
        Map the datasource parameters with broker parameters

        :param sender:
        :param kwargs:
        :return:
    """
    from basin3d.models import MeasurementVariable, DataSource, DataSourceMeasurementVariable

    for datasource in DataSource.objects.all():

        for variable_mapping in __iterate_measurement_mapping(datasource.plugin.get_plugin()):
            try:
                broker_id = MeasurementVariable.objects.get(id=variable_mapping['broker_id'])
                datasource_parameter = DataSourceMeasurementVariable()
                datasource_parameter.measure_variable = broker_id
                datasource_parameter.datasource = datasource
                datasource_parameter.name = variable_mapping['datasource_name']
                datasource_parameter.save()

            except IntegrityError:
                # This object has already been loaded
                pass

            except MeasurementVariable.DoesNotExist as e:
               print("Not Found Measurement Variable '{}' for Data Source '{}': {}".format(variable_mapping['broker_id'],
                                                                                         datasource.name, str(e)), file=sys.stderr)


def __iterate_measurement_mapping(plugin):
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
        mapping_file = os.path.join(plugin_file_path,"mapping_{}.csv".format(plugin.get_meta().id.lower()))
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
            raise Exception("There are no measurement variables ({}) mapped for this plugin {}".format(mapping_file, plugin.pythonpath))

    else:
        raise Exception("File path does not exist for plugin {}".format(plugin.pythonpath))


class Basin3DConfig(AppConfig):
    name = 'basin3d'

    def ready(self):

        # Execute the post migration scripts
        post_migrate.connect(load_measurment_objects, sender=self)
        post_migrate.connect(load_data_sources, sender=self)
        post_migrate.connect(load_datasource_parameters, sender=self)


