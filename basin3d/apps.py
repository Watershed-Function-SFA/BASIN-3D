import importlib

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
        print("Updated Data Source '{}'".format(plugin.get_meta().id))
        datasource.name = plugin.get_meta().id
        datasource.location = plugin.get_meta().location
        datasource.id_prefix = plugin.get_meta().id_prefix
        datasource.plugin = plugin_model
        datasource.save()


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
    from basin3d.models import MeasurementVariable, Measurement, SamplingMedium, MeasurementApproach

    # Load the Sampling Mediums
    for sm in SamplingMedium.SAMPLING_MEDIUMS:
        try:
            obj = SamplingMedium(name=sm)
            obj.save()
            print("Registered SamplingMedium '{}'".format(obj.name))
        except IntegrityError:
            pass

    # Load the Measurement Approaches
    for ma in MeasurementApproach.APPROACHES:
        try:
            obj = MeasurementApproach(name=ma)
            obj.save()
            print("Registered MeasurementApprach '{}'".format(obj.name))
        except IntegrityError:
            pass

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
                    print("Registered MeasurementVariable '{}'".format(p.id))
                except IntegrityError as e:

                    # We don't care about the Integrity Errors
                    pass
        else:
            print("There are no MEASUREMENT_VARIABLES to load")

        if hasattr(app_plugins, "MEASUREMENTS"):
            for m in app_plugins.MEASUREMENTS:
                try:
                    sm = None
                    try:
                        sm = SamplingMedium.objects.get(name=m["sampling_medium"])
                    except SamplingMedium.DoesNotExist:
                        sm = SamplingMedium(m["sampling_medium"])
                        sm.save()

                    ma = None
                    try:
                        ma = MeasurementApproach.objects.get(name=m["measurement_approach"])
                    except SamplingMedium.DoesNotExist:
                        ma = MeasurementApproach(m["measurement_approach"])
                        ma.save()

                    m["sampling_medium"] = sm
                    m["measurement_approach"] = ma

                    obj = Measurement(**m)
                    obj.save()
                    print("Registered Measurement '{} {}'".format(obj.variable_id, obj.description))
                except IntegrityError as e:

                    # We don't care about the Integrity Errors
                    pass
        else:
            print("There are no MEASUREMENTS to load")


def load_datasource_parameters(sender,**kwargs):
    """
        Map the datasource parameters with broker parameters

        :param sender:
        :param kwargs:
        :return:
    """
    from basin3d.models import MeasurementVariable, DataSource, DataSourceMeasurementVariable

    for datasource in DataSource.objects.all():

        for id, param in datasource.plugin.get_plugin().get_meta().measure_variable_map.items():
            try:
                broker_param = MeasurementVariable.objects.get(id=id)
                datasource_parameter = DataSourceMeasurementVariable()
                datasource_parameter.measure_variable = broker_param
                datasource_parameter.datasource = datasource
                datasource_parameter.name = param
                datasource_parameter.save()
                print("Registered Measurement Variable '{}' for Data Source '{}'".format(id,
                                                                                         datasource.name))
            except IntegrityError as e:
                # We don't care about the Integrity Errors
                pass


class Basin3DConfig(AppConfig):
    name = 'basin3d'

    def ready(self):

        ## Execute the post migration scripts
        post_migrate.connect(load_data_sources, sender=self)
        post_migrate.connect(load_measurment_objects, sender=self)
        post_migrate.connect(load_datasource_parameters, sender=self)


