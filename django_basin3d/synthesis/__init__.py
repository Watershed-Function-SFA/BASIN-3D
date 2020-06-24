"""
`django_basin3d.synthesis`
*******************

.. currentmodule:: django_basin3d.synthesis

:synopsis: The high level BASIN-3D synthesis models.
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>
:module author: Charuleka Varadharajan <cvaradharajan@lbl.gov>


* :py:mod:`~django_basin3d.synthesis.models` - defines the synthesis domain models that are brokered and synthesized by the custom :class:`~django_basin3d.plugins.DataSourcePluginPoint`.
* :py:mod:`~django_basin3d.synthesis.viewsets` - Controllers for BASIN-3D REST api



"""
from . import serializers

__all__ = ['serializers']
