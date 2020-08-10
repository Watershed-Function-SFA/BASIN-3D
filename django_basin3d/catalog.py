import importlib
import sys
from typing import Iterator, List, Optional

import django
from django.conf import settings
from django.db import IntegrityError, OperationalError

from basin3d.core.catalog import CatalogBase, CatalogException
from basin3d.core.models import DataSource, ObservedProperty, ObservedPropertyVariable
from basin3d.core.plugin import PluginMount


class CatalogDjango(CatalogBase):

    def __init__(self, variable_filename: str = 'basin3d_variables_hydrology.csv'):
        super().__init__(variable_filename)

    def is_initialized(self) -> bool:
        """Has the catalog been initialized?"""

        try:
            from django_basin3d.models import DataSource
            return DataSource.objects.count() > 0
        except ImportError:
            return False

    def _convert_django_observed_property_variable(self, django_opv) -> Optional[ObservedPropertyVariable]:
        """
        Convert django observed property variable to basin3d
        :param django_opv:
        :return:
        """
        if django_opv:
            return ObservedPropertyVariable(
                basin3d_id=django_opv.basin3d_id,
                full_name=django_opv.full_name,
                categories=django_opv.categories.split(",")
            )
        return None

    def _convert_django_observed_property(self, django_op) -> Optional[ObservedProperty]:
        """
        Convert django observed property to basin3d
        :param django_op:
        :return:
        """
        if django_op:

            from django_basin3d import models as django_models
            try:

                op = django_models.ObservedProperty.objects.get(datasource=django_op.datasource,
                                                                observed_property_variable=django_op.observed_property_variable)
                return ObservedProperty(
                    sampling_medium=op.sampling_medium.name,
                    datasource_variable=django_op.name,
                    datasource_description=django_op.datasource.name,
                    observed_property_variable=self._convert_django_observed_property_variable(
                        django_op.observed_property_variable),
                    datasource=DataSource(django_op.datasource.name, django_op.datasource.name,
                                          django_op.datasource.id_prefix, django_op.datasource.location)
                )
            except django_models.ObservedProperty.DoesNotExist:
                return None
            except Exception as e:
                if not e.__class__.__name__ == 'DoesNotExist':
                    raise e

        return None

    def _get_observed_property_variable(self, basin3d_id) -> Optional[ObservedPropertyVariable]:
        """
        Access a single observed property variable

        :param basin3d_id: the observed property variable identifier
        :return:
        """
        from django_basin3d import models as django_models

        try:
            opv = django_models.ObservedPropertyVariable.objects.get(basin3d_id=basin3d_id)
            return self._convert_django_observed_property_variable(opv)
        except django_models.ObservedProperty.DoesNotExist:
            return None
        except Exception as e:
            if not e.__class__.__name__ == 'DoesNotExist':
                raise e
            return None

    def _get_observed_property(self, datasource_id, basin3d_id, datasource_variable_id) -> Optional[ObservedProperty]:
        """
        Access a single observed property

        :param datasource_id:  datasource identifier
        :param basin3d_id:  BASIN-3D variable identifier
        :param datasource_variable_id: datasource variable identifier
        :return:
        """
        from django_basin3d import models as django_models
        try:

            op = django_models.DataSourceObservedPropertyVariable.objects.get(
                datasource__name=datasource_id,
                name=datasource_variable_id,
                observed_property_variable_id=basin3d_id)
            return self._convert_django_observed_property(op)
        except django_models.ObservedProperty.DoesNotExist:
            return None
        except Exception as e:
            if not e.__class__.__name__ == 'DoesNotExist':
                raise e
            return None

    def find_observed_property(self, datasource_id, variable_name) -> Optional[ObservedProperty]:
        """
        Get the measurement to the specified variable_name

        :param variable_name: the variable name to get the :class:`~basin3d.models.ObservedProperty` for
        :return: :class:`~basin3d.models.ObservedProperty`
        """
        if not self.is_initialized():
            raise CatalogException("Variable Store has not been initialized")

        from django_basin3d import models as django_models
        try:

            op = django_models.DataSourceObservedPropertyVariable.objects.get(datasource__name=datasource_id,
                                                                              observed_property_variable_id=variable_name)
            return self._convert_django_observed_property(op)
        except django_models.DataSourceObservedPropertyVariable.DoesNotExist:
            return None
        except Exception as e:
            if not e.__class__.__name__ == 'DoesNotExist':
                raise e
            return None

    def find_observed_properties(self, datasource_id=None, variable_names: List[str] = None) -> Iterator[ObservedProperty]:
        """
        Get the observed properties to the specified variable_names and datasource

        :param variable_names: the variable names to get the :class:`~basin3d.models.ObservedProperty` for
        :type variable_names: list
        :param datasource_id: The datasource to filter by

        :return: :class:`~basin3d.models.ObservedProperty`
        """
        if not self.is_initialized():
            raise CatalogException("Variable Store has not been initialized")

        from django_basin3d import models as django_models

        # Setup the search parameters
        query_params = {}
        if datasource_id:
            query_params["datasource__name"] = datasource_id
        if variable_names:
            query_params["observed_property_variable_id__in"] = variable_names

        try:
            for op in django_models.DataSourceObservedPropertyVariable.objects.filter(**query_params):
                yield self._convert_django_observed_property(op)
        except django_models.DataSourceObservedPropertyVariable.DoesNotExist:
            return None
        except Exception as e:
            if not e.__class__.__name__ == 'DoesNotExist':
                raise e
            return None

    def find_observed_property_variable(self, datasource_id, variable_name, from_basin3d=False) -> Optional[ObservedPropertyVariable]:
        """
        Convert the given name to either BASIN-3D from :class:`~basin3d.models.DataSource`
        variable name or the other way around.

        :param variable_name:  The :class:`~basin3d.models.ObservedPropertyVariable`
            name to convert
        :param: from_basin3d: boolean that says whether the variable name is a
           BASIN-3D variable. If not, then this a datasource variable name.
        :type from_basin3d: boolean
        :return: A variable name
        :rtype: str
        """
        if not self.is_initialized():
            raise CatalogException("Variable Store has not been initialized")

        from django_basin3d import models as django_models
        try:
            if from_basin3d:
                # Convert from BASIN-3D to DataSource variable name
                obj = django_models.DataSourceObservedPropertyVariable.objects.get(
                    datasource__name=datasource_id,
                    observed_property_variable_id=variable_name)
                return self._convert_django_observed_property_variable(obj.observed_property_variable)
            else:
                # Convert from DataSource variable name to BASIN-3D
                obj = django_models.DataSourceObservedPropertyVariable.objects.get(
                    datasource__name=datasource_id,
                    name=variable_name)
                return self._convert_django_observed_property_variable(obj.observed_property_variable)
        except django_models.DataSourceObservedPropertyVariable.DoesNotExist:
            return None
        except Exception as e:
            if not e.__class__.__name__ == 'DoesNotExist':
                raise e
            return None

    def find_observed_property_variables(self, datasource_id=None, variable_names=None, from_basin3d=False) -> Iterator[ObservedPropertyVariable]:
        """
        Convert the given list of names to either BASIN-3D from :class:`~basin3d.models.DataSource`
        variable name or the other way around.

        :param variable_names:  The :class:`~basin3d.models.ObservedPropertyVariable`
             names to convert
        :type variable_names: iterable
        :param: from_basin3d: boolean that says whether the variable name is a
            BASIN-3D variable. If not, then this a datasource variable names.
        :type from_basin3d: boolean
        :return: list of variable names
        :rtype: iterable
        """

        if not self.is_initialized():
            raise CatalogException("Variable Store has not been initialized")

        from django_basin3d import models as django_models

        # Setup the search parameters
        query_params = {}
        if datasource_id:
            query_params["datasource__name"] = datasource_id

        if from_basin3d and variable_names:
            if variable_names:
                query_params["observed_property_variable_id__in"] = set(variable_names)

        elif variable_names:
            if variable_names:
                query_params["name__in"] = set(variable_names)

        # Return all available variables
        for o in django_models.DataSourceObservedPropertyVariable.objects.filter(**query_params):
            yield self._convert_django_observed_property_variable(o.observed_property_variable)

    def _init_catalog(self):
        """
        Initialize the catalog database

        :return:
        """
        if not self.is_initialized():
            from django_basin3d import models as django_models

            # Load the sampling medium
            self._load_sampling_mediums()

            # Now create the Datasource objects in the data base
            from basin3d.core.plugin import PluginMount
            for name, plugin in PluginMount.plugins.items():
                module_name = plugin.__module__
                class_name = plugin.__name__

                print("Loading Plugin = {}.{}".format(module_name, class_name))

                try:
                    datasource = django_models.DataSource.objects.get(name=plugin.get_meta().id)
                except django_models.DataSource.DoesNotExist:
                    print("Registering NEW Data Source Plugin '{}.{}'".format(module_name, class_name))
                    datasource = django_models.DataSource()
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

    def _load_sampling_mediums(self):
        """
        Load the predefined sampling mediums in the database
        :param sender:
        :param kwargs:
        :return:
        """
        # Load the Sampling Mediums
        from basin3d.core.types import SamplingMedium
        from django_basin3d import models as django_models
        for sm in SamplingMedium.SAMPLING_MEDIUMS:
            try:
                obj = django_models.SamplingMedium(name=sm)
                obj.save()
                print("Created SamplingMedium {}".format(sm))
            except IntegrityError:
                # This object has already been loaded
                pass
            except Exception as e:
                print("Error Registering SamplingMedium '{}': {}".format(sm, str(e)), file=sys.stderr)

    def _insert(self, record):
        """
        :param record:
        """
        from django_basin3d import models as django_models

        if self.is_initialized():
            if isinstance(record, ObservedPropertyVariable):
                try:
                    p = django_models.ObservedPropertyVariable()
                    p.basin3d_id = record.basin3d_id
                    p.full_name = record.full_name
                    p.categories = ",".join(record.categories)
                    p.save()

                except IntegrityError:

                    # This object has already been loaded
                    pass

                except Exception as e:

                    print("Error Registering ObservedPropertyVariable '{}': {}".format(record.basin3d_id, str(e)))
            elif isinstance(record, ObservedProperty):

                datasource = django_models.DataSource.objects.get(name=record.datasource.id)
                sm = django_models.SamplingMedium.objects.get(name=record.sampling_medium)
                v = None
                try:
                    v = django_models.ObservedPropertyVariable.objects.get(
                        basin3d_id=record.observed_property_variable.basin3d_id)
                    op = django_models.ObservedProperty.objects.get(observed_property_variable=v, datasource=datasource)
                    op.sampling_medium = record.sampling_medium
                    op.description = record.datasource_description
                    op.save()
                    print("Created Observed Property {} for {}".format(v, datasource))
                except django_models.ObservedProperty.DoesNotExist:

                    op = django_models.ObservedProperty(sampling_medium=sm,
                                                        description=record.observed_property_variable.full_name,
                                                        datasource=datasource,
                                                        observed_property_variable=v)
                    op.save()
                    print("Created Observed Property {} for {}".format(v, datasource))
                except IntegrityError as ie:
                    # Its OK that is has already been created
                    print(str(ie), file=sys.stderr)

                except Exception as e:

                    print(
                        "Error Registering Measurement '{} {}': {}".format(record.observed_property_variable.basin3d_id,
                                                                           record.observed_property_variable.full_name,
                                                                           str(e)))
                try:
                    datasource_parameter = django_models.DataSourceObservedPropertyVariable()
                    datasource_parameter.observed_property_variable = v
                    datasource_parameter.datasource = datasource
                    datasource_parameter.name = record.datasource_variable
                    datasource_parameter.save()

                except IntegrityError:
                    # This object has already been loaded
                    pass

                except Exception as e:
                    print("Error Registering DataSource Observed Property Variable '{}' for Data Source '{}': {}".
                          format(record.observed_property_variable.basin3d_id, datasource.name, str(e)),
                          file=sys.stderr)
        else:
            raise CatalogException('Could not insert record.  Catalog not initialize')


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
            print(f"Loaded {django_app} plugins")

            catalog = CatalogDjango()
            catalog.initialize([v(catalog) for v in PluginMount.plugins.values()])
        except ImportError:
            pass
        except OperationalError as oe:
            print(f"Operational Error '{oe}'' - Most likely happens on a reverse migration.")


