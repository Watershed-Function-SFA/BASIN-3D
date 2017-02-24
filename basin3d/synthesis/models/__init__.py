"""
`basin3d.synthesis.models`
**************************

.. currentmodule:: basin3d.synthesis.models

:synopsis: Classes to represent generic observation data concepts

* :class:`Base` - The base model class that all synthesis extend from

----------------------------------

"""


class Base(object):
    """
    Base synthesis model class
    """
    __attributes = {}

    def __init__(self, datasource, **kwargs):

        self.__attributes = self.__dict__.keys()
        self.datasource = datasource
        if not isinstance(kwargs, dict):
            raise TypeError("Expected a dict")

        if len(kwargs.keys()) > 0 and self.__attributes.isdisjoint(set(kwargs.keys())):
            bad_attributes = set(kwargs.keys()).difference(self.__attributes)
            raise ValueError("Invalid argument(s) for Sites: {}".format(bad_attributes))

        if 'datasource_ids' in kwargs.keys():
            for id in kwargs['datasource_ids']:
                if kwargs[id]:
                    kwargs[id] = "{}-{}".format(self.datasource.id_prefix, kwargs[id])

        if 'id' in kwargs:
            kwargs["id"] = "{}-{}".format(self.datasource.id_prefix, kwargs['id'])

        self.__dict__.update(kwargs)


class Person(Base):
    """A person

    Attributes:
        *id:* string
        *first_name:* string
        *last_name:* string
        *email:* string
        *institution:* string
    """

    def __init__(self, **kwargs):
        self.id = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.institution = None

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)


__all__ = ['field', 'simulations', 'measurement', 'Base']
