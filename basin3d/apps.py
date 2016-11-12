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
        datasource = DataSource.objects.filter(name=plugin.get_meta().id)
        if len(datasource) ==0:
            print("Registering Data Source '{}'".format(plugin.get_meta().id))
            d = DataSource()
            d.name = plugin.get_meta().id
            d.location = plugin.get_meta().location
            d.credentials = plugin.get_meta().credentials_format
            d.plugin = plugin_model
            d.save()


def load_parameters(sender, **kwargs):
    """
        Load the Broker paramters from the registered plugins.

        :param sender:
        :param kwargs:
        :return:
    """
    from djangoplugins.models import Plugin
    from basin3d.models import MeasurementVariable

    plugins = Plugin.objects.all()
    for plugin in plugins:
        plugin_path = plugin.pythonpath
        idx = plugin_path.index('plugins')
        module_name = plugin_path[0:idx+len('plugins')]
        app_plugins = importlib.import_module(module_name)
        for param in app_plugins.MEASUREMENT_VARIABLES:
            try:
                p = MeasurementVariable()
                p.id=param[0]
                p.full_name = param[1]
                p.categories = ",".join(param[2])
                p.save()
                print("Registered Measurement'{}'".format(p.id))
            except IntegrityError as e:

                # We don't care about the Integrity Errors
                pass


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
                print("Registered  Measurement Variable '{}' for Data Source '{}'".format(id,datasource.name))
            except IntegrityError as e:
                # We don't care about the Integrity Errors
                pass


class Basin3DConfig(AppConfig):
    name = 'basin3d'

    def ready(self):

        ## Execute the post migration scripts
        post_migrate.connect(load_data_sources, sender=self)
        post_migrate.connect(load_parameters, sender=self)
        post_migrate.connect(load_datasource_parameters, sender=self)


