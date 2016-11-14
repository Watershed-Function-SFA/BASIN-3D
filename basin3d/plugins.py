"""


"""
from basin3d import synthesis
from basin3d.apps import Basin3DConfig
from django.apps import apps
from djangoplugins.point import PluginPoint


class DataSourcePluginViewMeta(type):
    """
    Metaclass for DataSource plugin views.  The should be registered in a subclass of
    :class:`basin3d.plugins.DataSourcePluginPoint` in attribute `plugin_view_classes`.
    """

    def __new__(cls, name, parents, dct):

        # If there is an init method, we want to modify it
        # to accept a DataSource instance
        old_init=None
        if "__init__" in dct:
            old_init = dct["__init__"]

        def new_init(self, *args, **kwargs):

            DataSource = apps.get_app_config(Basin3DConfig.name).get_model('DataSource')

            # if there is an init, execute it
            if old_init:
                old_init(self, *args, **kwargs) # original init

            if not args and len(args) == 0 and not isinstance(args[0],DataSource):
                raise ValueError("Must specify an argument of type {}".format(DataSource))

            self.datasource = args[0]

        dct["__init__"] = new_init # replace the original init

        return type.__new__(cls, name, parents, dct)

    def __init__(cls, name, parents, dct):

        if "synthesis_model_class" in dct:
            synthesis_model_class = dct["synthesis_model_class"]
            if isinstance(synthesis_model_class, str):
                class_name_list = synthesis_model_class.split(".")
                module_name = synthesis_model_class.replace(".{}".format(class_name_list[-1]), "")
                module = __import__(module_name)
                synthesis_model_class = getattr(module, class_name_list[-1])

            if not isinstance(synthesis_model_class, synthesis.models.Base):
                ValueError("synthesis_model_class for {} must extend from synthesis.Base".format(
                    DataSourcePluginViewMeta.__name__))

        else:
            raise ValueError("Must define a synthesis_model_class for {}".format(DataSourcePluginViewMeta.__name__))

        # we need to call type.__init__ to complete the initialization
        super(DataSourcePluginViewMeta, cls).__init__(name, parents, dct)


class DataSourcePluginPoint(PluginPoint):
    """
    Base class for DataSourcePlugins.
    """

    @classmethod
    def get_meta(cls):
        """
        Gets the DataSourceMeta internal class that should be defined by subclasses.
        Raises an error if it is not found
        :return:
        """
        meta = getattr(cls, 'DataSourceMeta', None)

        if not meta:
            raise ValueError("Must define inner class DatasSourceMeta for {}".format(cls))
        return meta

    @classmethod
    def get_datasource(cls):
        """
        Get the `basin3d.models.DataSource` record for the subclass of this Plugin.
        :return:
        """
        meta = cls.get_meta()
        datasource_id = getattr(meta, 'id', None)
        if datasource_id:
            DataSource = apps.get_app_config(Basin3DConfig.name).get_model('DataSource')
            obj = DataSource.objects.get(name=datasource_id)
            return obj
        else:
            raise ValueError("{}.DataSourceMeta does not define an 'id'.")

    @classmethod
    def get_plugin_views(cls):
        """
        Get the defined plugin_view_classes from the subclass.  These should be defined in
        `DataSourceMeta.plugin_view_subclass`. If not, an error is thrown
        :return:
        """
        view_classes = {}
        plugin_view_classes = getattr(cls, 'plugin_view_classes', None)
        if plugin_view_classes:
            for view_class in plugin_view_classes:
                view = view_class(cls.get_datasource())
                view_classes[view.synthesis_model_class] = view
        else:
            raise ValueError("{} does not define any plugin_view_classes.")

        return view_classes
