"""
`basin3d.synthesis`
*******************

.. currentmodule:: basin3d.synthesis

:synopsis: The high level BASIN-3D synthesis models.
:module author: Val Hendrix <vhendrix@lbl.gov>, Charuleka Varadharajan <cvaradharajan@lbl.gov>


Models
------

* :py:mod:`~basin3d.synthesis.models` - defines the synthesis domain models that are brokered and synthesized by the custom :class:`~basin3d.plugins.DataSourcePluginPoint`.
* :py:mod:`~basin3d.synthesis.models.simulations` - Classes to represent Simulation/Modeling Concepts


Serializers
-----------


ViewSets
--------

TBD

"""
from . import models
__all__ = ['models']