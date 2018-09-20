import importlib

import sys

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
    from basin3d.models import SamplingMedium, MeasurementApproach, Measurement

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

        if hasattr(plugin.get_meta(), "MEASUREMENTS"):
            for m in plugin.get_meta().MEASUREMENTS:
                try:
                    try:
                        sm = SamplingMedium.objects.get(name=m["sampling_medium"])
                    except SamplingMedium.DoesNotExist:
                        sm = SamplingMedium(m["sampling_medium"])
                        sm.save()

                    try:
                        ma = MeasurementApproach.objects.get(name=m["approach"])
                    except SamplingMedium.DoesNotExist:
                        ma = MeasurementApproach(m["approach"])
                        ma.save()

                    m["sampling_medium"] = sm
                    m["approach"] = ma
                    m["datasource"] = datasource

                    obj = Measurement(**m)
                    obj.save()

                except Exception as e:

                    print("Error Registering Measurement '{} {}': {}".format(obj.variable_id, obj.description, str(e)))
        else:
            print("There are no MEASUREMENTS to load")


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
    from basin3d.models import MeasurementVariable, SamplingMedium, MeasurementApproach

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

    # Load the Measurement Approaches
    for ma in MeasurementApproach.APPROACHES:
        try:
            obj = MeasurementApproach(name=ma)
            obj.save()

        except IntegrityError:
            # This object has already been loaded
            pass

        except Exception as e:
            print("Error Registering MeasurementApproach '{}': {}".format(obj.name, str(e)), file=sys.stderr)

    plugins = Plugin.objects.all()
    for plugin in plugins:
        plugin_path = plugin.pythonpath
        idx = plugin_path.index('plugins')
        module_name = plugin_path[0:idx+len('plugins')]
        app_plugins = importlib.import_module(module_name)

        if hasattr(app_plugins, "MEASUREMENT_VARIABLES"):
            for param in app_plugins.MEASUREMENT_VARIABLES:
                try:
                    p = MeasurementVariable()
                    p.id = param[0]
                    p.full_name = param[1]
                    p.categories = ",".join(param[2])
                    p.save()

                except IntegrityError:

                    # This object has already been loaded
                    pass

                except Exception as e:

                    print("Error Registering MeasurementVariable '{}': {}".format(param[0], str(e)))
        else:
            print("There are no MEASUREMENT_VARIABLES to load")


def load_datasource_parameters(sender,**kwargs):
    """
        Map the datasource parameters with broker parameters

        :param sender:
        :param kwargs:
        :return:
    """
    from basin3d.models import MeasurementVariable, DataSource, DataSourceMeasurementVariable

    for datasource in DataSource.objects.all():

        for id, param in datasource.plugin.get_plugin().get_meta().MEASURE_VARIABLE_MAP.items():
            try:
                broker_param = MeasurementVariable.objects.get(id=id)
                datasource_parameter = DataSourceMeasurementVariable()
                datasource_parameter.measure_variable = broker_param
                datasource_parameter.datasource = datasource
                datasource_parameter.name = param
                datasource_parameter.save()

            except IntegrityError:
                # This object has already been loaded
                pass

            except MeasurementVariable.DoesNotExist as e:
               print("Not Found Measurement Variable '{}' for Data Source '{}': {}".format(id,
                                                                                         datasource.name, str(e)), file=sys.stderr)


class Basin3DConfig(AppConfig):
    name = 'basin3d'

    def ready(self):

        ## Execute the post migration scripts
        post_migrate.connect(load_measurment_objects, sender=self)
        post_migrate.connect(load_data_sources, sender=self)
        post_migrate.connect(load_datasource_parameters, sender=self)


