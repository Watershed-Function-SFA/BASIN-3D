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
    Base synthesis model class.  All classes that extend this are immutable
    """
    __attributes = {}

    def __init__(self, datasource, **kwargs):

        self.__attributes = {x for x in self.__dict__.keys()}
        self.__attributes.add("datasource_ids")
        self.datasource = datasource
        if not isinstance(kwargs, dict):
            raise TypeError("Expected a dict")

        # Check for invalid arguments
        bad_attributes = set(kwargs.keys()).difference(self.__attributes)
        if len(bad_attributes) > 0:
            raise ValueError("Invalid argument(s) for {} : {}".format(self.__class__.__name__,
                                                                      ",".join(bad_attributes)))

        # any ids listed should have the DataSource.id_prefix
        if 'datasource_ids' in kwargs.keys():
            for id in kwargs['datasource_ids']:
                if kwargs[id]:
                    kwargs[id] = "{}-{}".format(self.datasource.id_prefix, kwargs[id])

        if "id" in kwargs and datasource:
            kwargs["id"] = "{}-{}".format(self.datasource.id_prefix, kwargs["id"])

        self.__dict__.update(kwargs)

        def __setattr__(self, *ignore_args):
            """
            This has been disabled.  The class is immutable

            :param ignore_args:
            :return:
            """
            raise AttributeError("{} is Immutable".format(self.__class__.__name__))

        def __delattr__(self, *ignore_args):
            """
               This has been disabled.  The class is immutable

               :param ignore_args:
               :return:
               """
            raise AttributeError("{} is Immutable".format(self.__class__.__name__))

        self.__setattr__ = __setattr__
        self.__delattr__ = __delattr__


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
