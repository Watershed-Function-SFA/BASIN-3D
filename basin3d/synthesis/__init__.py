"""
`basin3d.synthesis`
*******************

.. currentmodule:: basin3d.synthesis

:synopsis: The high level BASIN-3D synthesis models.
:module author: Val Hendrix <vhendrix@lbl.gov>, Charuleka Varadharajan <cvaradharajan@lbl.gov>


* :py:mod:`~basin3d.synthesis.models` - defines the synthesis domain models that are brokered and synthesized by the custom :class:`~basin3d.plugins.DataSourcePluginPoint`.
* :py:mod:`~basin3d.synthesis.serializers` - Classes that render :mod:`basin.synthesis.models` from Python objects to `JSON` and back again.
* :py:mod:`~basin3d.synthesis.viewsets` - Controllers for BASIN-3D REST api



"""
from . import models, query

__all__ = ['models', 'query']


