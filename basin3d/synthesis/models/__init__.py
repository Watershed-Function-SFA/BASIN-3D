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

        self._datasource_ids = None
        self._datasource = datasource
        self._id = None
        self._original_id = None

        if not isinstance(kwargs, dict):
            raise TypeError("Expected a dict")

        # any ids listed should have the DataSource.id_prefix
        if 'datasource_ids' in kwargs.keys():
            for id in kwargs['datasource_ids']:
                if kwargs[id]:
                    kwargs[id] = "{}-{}".format(self.datasource.id_prefix, kwargs[id])
        if "id" in kwargs and datasource:
            kwargs["original_id"] = kwargs["id"]
            kwargs["id"] = "{}-{}".format(self.datasource.id_prefix, kwargs["id"])

        # Now that we have massaged the incoming key/value pairs, let's
        # set them in the
        bad_attributes = []
        for key, value in kwargs.items():

            if not hasattr(self,key):
                bad_attributes.append(key)
            else:
                setattr(self, key, value)

        if len(bad_attributes) > 0:
            raise ValueError("Invalid argument(s) for {} : {}".format(self.__class__.__name__,
                                                                      ",".join(bad_attributes)))

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

    @property
    def datasource_ids(self):
        return self._datasource_ids

    @datasource_ids.setter
    def datasource_ids(self, value):
        self._datasource_ids = value

    @property
    def datasource(self):
        return self._datasource

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def original_id(self):
        return self._original_id

    @original_id.setter
    def original_id(self, value):
        self._original_id = value


class Person(Base):
    """A person

    Attributes:
        *id:* string
        *first_name:* string
        *last_name:* string
        *email:* string
        *institution:* string
        *role:* string
    """

    def __init__(self, **kwargs):
        self.id = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.institution = None
        self.role = None

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)


__all__ = ['field', 'measurement', 'Base']
