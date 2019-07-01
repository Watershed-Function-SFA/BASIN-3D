"""
`basin3d.synthesis`
*******************

.. currentmodule:: basin3d.synthesis

:synopsis: The high level BASIN-3D synthesis models.
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>
:module author: Charuleka Varadharajan <cvaradharajan@lbl.gov>


* :py:mod:`~basin3d.synthesis.models` - defines the synthesis domain models that are brokered and synthesized by the custom :class:`~basin3d.plugins.DataSourcePluginPoint`.
* :py:mod:`~basin3d.synthesis.viewsets` - Controllers for BASIN-3D REST api



"""
from . import models, query, viewsets, serializers

__all__ = ['models', 'query', 'viewsets', 'serializers']
