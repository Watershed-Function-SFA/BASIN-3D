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
from basin3d.version import __version__, __release__

# application loads this AppConfig subclass by default
# when basin3d is added to INSTALLED_APPS
default_app_config = 'basin3d.apps.Basin3DConfig'
