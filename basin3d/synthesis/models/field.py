"""
`basin3d.synthesis.models.field`
********************************

.. currentmodule:: basin3d.synthesis.models.field

:synopsis: Classes to represent Multi-scale Spatial Hierarchy for Field Observations

* :class:`Region` - An arbitrary area

----------------------------------

"""

from basin3d.synthesis.models import Base


class Region(Base):
    """
    A Region is any arbitrary area - not necessarily associated with any
    observations - e.g. a watershed, a city

    Attributes:
        - *id:* string
        - *name:* string
        - *description:* string
        - *geom:* polygon
    """

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.name = None
        self.description = None
        self.geom = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)
