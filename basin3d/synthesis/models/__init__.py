"""
`basin3d.synthesis.models`
**************************

.. currentmodule:: basin3d.synthesis.models

:synopsis: The BASIN-3D Synthesis Models
:module author: Val Hendrix <vhendrix@lbl.gov>

Classes to represent generic observation data concepts

* :class:`Base` - The base model class that all synthesis extend from

----------------------------------

"""

class Base(object):
    """
    Base synthesis model class
    """
    __attributes = {}

    def __init__(self, **kwargs):

        self.__attributes = self.__dict__.keys()

        if not isinstance(kwargs, dict):
            raise TypeError("Expected a dict")

        if len(kwargs.keys()) > 0 and self.__attributes.isdisjoint(set(kwargs.keys())):
            bad_attributes = set(kwargs.keys()).difference(self.__attributes)
            raise ValueError("Invalid argument(s) for Sites: {}".format(bad_attributes))

        self.__dict__.update(kwargs)


__all__ = ['simulations', 'Base']
