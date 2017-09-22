"""
==============================
BASIN-3D Data Source REST APIs
==============================
.. currentmodule:: basin3d

:platform: Unix, Mac
:synopsis: All BASIN-3D REST api calls are read-only (GET). The browsable API may be accessed at the root URL of the application.
:module author: Val Hendrix <vhendrix@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top


Synthesis API
*************
Synthesis is  the process of converting multiple heterogeneous data sources into a single uniform format.
This section describes BASIN-3D synthesis REST API.

Data Sources
------------
BASIN-3D Data sources definitions.  All data sources defined are available for synthesis in the
subesequent APIs

| `/synthesis/datasources --` Returns a list of data sources.
| `/synthesis/datasources/:id --` Get a single data source

**Attributes:**
    - *name:* unique name for this data source
    - *location:* web resource location of the data source
    - *id_prefix:* a unique iset of characters to prefix ids for this data source

**URLs**
  + url -- for detail on a single data source
  + direct_path -- Access the direct API for this data source


Variables
---------
Common names for measurement variables. Data source measurement variables are mapped thes synthesized
variables.

| `/synthesis/variables --` Returns a list of variables.
| `/synthesis/variables/:id --` Get a single variable

**Attributes:**
    - *full_name:* string
    - *categories:* ordered string list of categories

**URLs**
  + url -- for detail on a single measurement variable


Regions
-------
A Region is any arbitrary area - not necessarily associated with any
observations - e.g. a watershed, a city

| `/synthesis/regions --` Returns a list of regions.
| `/synthesis/regions/:id --` Get a single region

**Attributes:**
    - *id:* string
    - *name:* string
    - *description:* string
    - *url:* polygon

**URLs**
  + url -- for detail on a single city
  + model_domains -- to list all river systems for a city


Measurements and Results
------------------------

Measurements
++++++++++++
Defining the attributes for a single/multiple measurements

**Attributes:**
    - *id:* string,
    - *description:* id
    - *variable:* string
    - *sampling_medium:* enum (atmosphere, surface water, soil/sediment, soil gas, groundwater), atmosphere
    - *measurement_approach:* enum (sensor, manual), sensor

**URLs**
  + url -- for detail on a single measurement


Data Point Groups
+++++++++++++++++
Series of data points grouped by time, space, model, sample  etc. Anything specified at the
group  level automatically applies to the individual data point.

**Attributes:**
    - *id:* string
    - *start_time:* datetime,  survey start time (month/year)
    - *end_time:* datetime, units: survey end time (month/year)
    - *utc_offset:* float (offset in hours)
    - *results:* Array of DataPoint objects

**URLs**
  + url -- for detail on a single data point group
  + data_points -- The data points associated to the current data point group
  + geographical_group -- The geographical group associated to the current data point group
  + measurement -- The measurement associated to the current data point group

Data Points
+++++++++++
Data Point (what, where, when??)

**Generic Attributes:**
    - *id:* string,
    - *unit:* Unit

**Time Series Attributes:**
    - *timestamp:* datetime,
    - *value:* float,
    - *units:* Unit  Cs137UID
    - *temporal_resolution:* enum(year, month, day, hour, minute, second, millisecond),
    - *reference:* string (start, middle, end),
    - *utc_offset:* float (offset in hours) - optional

**URLs**
  + url -- for detail on a single data point
  + geographical_group -- The geographical group associated to the current data point group
  + measurement -- The measurement associated to the current data point group

Direct API
**********
Bypass synthesis by accessing the data source APIs directly

| `/direct/ --` Returns a list of direct apis
| `/direct/:id_prefix --` Access a direct api for a datasource with the `:idprefix`

"""
import logging

logger = logging.getLogger(__name__)

__all__ = ['get_url']

# application loads this AppConfig subclass by default
# when basin3d is added to INSTALLED_APPS
default_app_config = 'basin3d.apps.Basin3DConfig'


def __insert_basin3d_defaults():
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


__insert_basin3d_defaults()


def get_url(url, params=None, headers=None, verify=False):
    """
    Send a GET request to the specified URL

    :param url:
    :param params: request parameters
    :param headers: request headers
    :param verify: verify SSL connection
    :return: Response
    """
    import requests
    response = requests.get(url, params=params, verify=verify, headers=headers)
    return response
