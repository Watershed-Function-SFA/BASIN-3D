"""
`basin3d`
*********
.. currentmodule:: basin3d

:platform: Unix, Mac
:synopsis: The high level BASIN-3D Django Framework.
:module author: Val Hendrix <vhendrix@lbl.gov>


Modules
-------

* :py:mod:`.admin` - defines the domain models that are managed by an administrator on the admin site.
    * **Data Sources** - Manage a :class:`basin3d.models.DataSource`
    * **Measurement Variables** - Manage a :class:`basin3d.models.MeasurementVariable`
    * **Data Source Measurement Variables** - Links a :class:`basin3d.models.DataSource` to a :class:`basin3d.models.MeasurementVariable`





---------------------
"""
import logging

from basin3d.version import __version__, __release__

logger = logging.getLogger(__name__)

# application loads this AppConfig subclass by default
# when basin3d is added to INSTALLED_APPS
default_app_config = 'basin3d.apps.Basin3DConfig'


def insert_basin3d_defaults():
    """
    Insert BASIN-3D default settings :class:`basin3d.settings`
    """

    from django.conf import global_settings, settings
    from basin3d import settings as basin3d_settings

    # Add the values from the application.settings module
    for key in dir(basin3d_settings):
        if key.isupper():


            # Add the defaults to the global setting
            setattr(global_settings, key, getattr(basin3d_settings, key))

            # only add default if they have not been set already
            # We don't want to override local setting
            if not hasattr(settings, key):
                setattr(settings, key, getattr(basin3d_settings, key))
            elif key in ['BASIN3D','REST_FRAMEWORK']:
                basin3d = getattr(basin3d_settings, key)
                local_basin3d = getattr(settings, key)
                for key in basin3d.keys():
                    if key not in local_basin3d:
                        local_basin3d[key]=basin3d[key]

insert_basin3d_defaults()


def get_url(url, params=None, headers=None, verify=False):
    import requests
    response = requests.get(url, params=params, verify=verify, headers=headers)
    from rest_framework import status
    if response.status_code == status.HTTP_200_OK:
        try:
            return response
        except Exception as e:
            logger.error("Datasource error {}: Invalid JSON return from url: {}".format(url,
                                                                            response.content))
            return None
    else:
        logger.error(
            "Datasource error {}: HTTP Error {} {}".format(url, response.status_code,
                                                           response.content))
    return None
