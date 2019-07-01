"""
==============================
BASIN-3D REST APIs
==============================
.. currentmodule:: basin3d

:platform: Unix, Mac
:synopsis: All BASIN-3D REST API calls are read-only (GET). The browsable API may be accessed at the root URL of the application.
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top


Synthesis API
*************
Synthesis is the process of converting multiple heterogeneous data sources into a single uniform format.
This section describes BASIN-3D synthesis REST API.

Data Sources
------------
BASIN-3D Data sources definitions.  All data sources defined are available for synthesis in the
subesequent APIs.

| `/synthesis/datasources --` Returns a list of data sources
| `/synthesis/datasources/:id --` Get a single data source

**Attributes:**
    - *name:* Unique name for the data source
    - *id_prefix:* A unique iset of characters to prefix ids for the data source
    - *location:* Location of the data source
    - *observed_property_variables:* Observed property variables for the data source

**URLs**
  + url -- URL with details for the data source
  + direct_path -- Access the direct API for the data source
  + check -- Validation URL for the data source connection


Observed Property Variables
---------------------------
Common names for observed property variables. A observed property variable defines what is
being measured. Data source observed property variables are mapped to these synthesized
observed property variables.

| `/synthesis/observedpropertyvariables --` Returns a list of observed property variables
| `/synthesis/observedpropertyvariables/:id --` Get a single observed property variable

**Attributes:**
    - *id:* Unique observed property variable identifier
    - *full_name:* Descriptive name for the observed property variable
    - *categories:* Categories of which the variable is a member, listed in hierarchical order
    - *datasources:* List of the data sources that define the current observed property variable

**URLs**
  + url -- URL with details for the observed property variable


Observed Properties
-------------------
Definition of the attributes for an observed property

| `/synthesis/observedproperty --` Returns a list of observed property variables
| `/synthesis/observedproperty/:id --` Get a single observed property variable

**Attributes:**
    - *observed_property_variable:* Observed property variable assigned to the observed property
    - *datasource:* Data source defining the observed property
    - *sampling_medium:* Medium in which the observed property is observed (WATER, GAS, SOLID_PHASE, OTHER, NOT_APPLICABLE)
    - *description:* Additional information about the observed property

**URLs**
  + url -- URL with details for the observed property


Monitoring Features
-------------------
A feature on which an observation is made. Features organized into spatial
hierarchies are described via the related_sampling_feature complex

| `/synthesis/monitoringfeatures --` Returns a list of monitoring features types
| `/synthesis/monitoringfeatures/:featuretype --` Returns a list of monitoring features of the specified feature type
| `/synthesis/monitoringfeatures/:featuretype/:id --` Get a single monitoring feature

**Attributes:**
    - *id:* Unique feature identifier
    - *name:* Feature name
    - *description:* Description of the feature
    - *feature_type:* Type of feature, supported feature types: REGION, SUBREGION, BASIN, SUBBASIN, WATERSHED, SUBWATERSHED, SITE, PLOT, HORIZONTAL PATH, VERTICAL PATH, POINT
    - *observed_property_variables:* list of observed variables made at the feature. Observed property variables are configured via the plugins.
    - *related_sampling_feature_complex:* List of related sampling_features. PARENT features are currently supported.
    - *shape:* Shape of the feature: POINT, CURVE, SURFACE, SOLID
    - *coordinates:* Location of feature in absolute and/or representative datum
    - *description_reference:* Additional information about the feature
    - *related_party:* List of people or organizations responsible for the feature
    - *utc_offset:* Coordinate Universal Time offset in hours

**URLs**
  + url -- URL with details for the feature


MeasurementTimeseriesTVPObservation
-----------------------------------
MeasurementTimeseriesTVPObservation: Series of measurement (numerical) observations
in TVP (time value pair) format grouped by time (i.e., a timeseries).
Attributes specified at the group level apply to all observations.

| `/synthesis/measurementtvptimeseries/?filters --` Get a single measurement timeseries TVP observation:

**Attributes:**
    - *id:* Observation identifier (optional)
    - *type:* type of observation = MEASUREMENT_TVP_TIMESERIES
    - *phenomenon_time:* Datetime of the observation, for a timeseries the start and end times can be provided
    - *utc_offset:* Coordinate Universal Time offset in hours (offset in hours), e.g., +9
    - *feature_of_interest:* feature on which the observation is being made
    - *feature_of_interest_type:* feature type of the feature of interest
    - *result_points:* observed values of the observed property being assessed in format of TVP (time value pair)
    - *time_reference_position:* position of timestamp in aggregated_duration (START, MIDDLE, END)
    - *aggregation_duration:* time period represented by observation (YEAR, MONTH, DAY, HOUR, MINUTE, SECOND)
    - *unit_of_measurement:* units in which the observation is reported
    - *statistic:* statistical property of the observation result (MEAN, MIN, MAX, TOTAL)
    - *result_quality:* quality assessment of the result (CHECKED, UNCHECKED)

**URLs**
  + url -- URL with details for the feature
  + observed_property -- URL for the observation's observed property

**Filters**
    - *monitoring_features (required):* comma separated list of monitoring_features ids
    - *observed_property_variables (required):* comma separated list of observed property variable ids
    - *start_date (required):* date YYYY-MM-DD
    - *end_date (optional):* date YYYY-MM-DD
    - *aggregation_duration (default: DAY):* enum (YEAR|MONTH|DAY|HOUR|MINUTE|SECOND)
    - *datasource (optional):* a single data source id prefix (e.g ?datasource=`datasource.id_prefix`)


Direct API
**********
Bypass synthesis by accessing the data source APIs directly

| `/direct/ --` Returns a list of direct APIs
| `/direct/:id_prefix --` Access a direct API for a datasource with the `:id_prefix`

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
            elif key in ['BASIN3D', 'REST_FRAMEWORK']:
                basin3d = getattr(basin3d_settings, key)
                local_basin3d = getattr(settings, key)
                for key in basin3d.keys():
                    if key not in local_basin3d:
                        local_basin3d[key] = basin3d[key]


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
    logger.debug("url:{}".format(response.url))
    return response


def post_url(url, params=None, headers=None, verify=False):
    """
    Send a POST request to the specified URL

    :param url:
    :param params: request parameters
    :param headers: request headers
    :param verify: verify SSL connection
    :return: Response
    """
    import requests
    response = requests.post(url, params=params, verify=verify, headers=headers)
    logger.debug("url:{}".format(response.url))
    return response


__all__ = ['synthesis']
