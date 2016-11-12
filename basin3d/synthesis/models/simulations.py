"""


`basin3d.synthesis.models.simulations`
**************************************

.. currentmodule:: basin3d.synthesis.models.simulations

:platform: Unix, Mac
:synopsis: The h BASIN-3D Synthesis Models
:module author: Val Hendrix <vhendrix@lbl.gov>

Classes to represent Simulation/Modeling Concepts (package basin3d.synthesis.models.simulations)


---------------------
"""
from basin3d.synthesis.models import Base


class Model(Base):
    """
        Defines the model being used

        Attributes:
            - *id:* string
            - *name:* string
            - *version:* string
            - *URL:* string
            - *dimensionality:* enum (1D, 2D, 3D)
    """

    def __init__(self, **kwargs):
        self.id = None
        self.version = None
        self.url = None  # this should be something else
        self.dimensionality = None

        # Initialize after the attributes have been set
        super().__init__(**kwargs)

    def __eq__(self, other):
        return self.id == other.id and self.version == other.version \
               and self.url == other.url and self.dimensionality == other.dimensionality


class ModelDomain(Base):
    """
        Specifies the area being modeled

        Attributes:
            - *model_domain_id:* string
            - *model_domain_name:* string
            - *geom:* Polygon
            - *meshes:* Array of :class:`~basin3d.synthesis.models.simulations.Mesh` objects
    """

    def __init__(self, **kwargs):
        self.model_domain_id = None
        self.model_domain_name = None
        self.url = None
        self.geom = None
        self.meshes = None

        # Initialize after the attributes have been set
        super().__init__(**kwargs)

    def __eq__(self, other):
        return self.model_domain_id == other.model_domain_id and self.model_domain_name == other.model_domain_name \
               and self.url == other.url and self.geom == other.geom


class Mesh(Base):
    """
        A sub-area within the model domain

        Attributes:
            - *mesh_id:* string
            - *parameters:* Array of :class:`~basin3d.synthesis.models.simulations.ModelParameter` objects
            - *initial_conditions:* Array of :class:`basin3d.models.MeasurementVariable` objects
    """

    def __init__(self, **kwargs):
        self.mesh_id = None
        self.parameters = []
        self.initial_conditions = []

        # Initialize after the attributes have been set
        super().__init__(**kwargs)

    def __eq__(self, other):
        return self.mesh_id == other.mesh_id


class ModelParameter(Base):
    """
        Parameters set in the equation the model is solving.

        Attributes:
            - *id:* string
            - *name:* string
            - *value:* float
    """

    def __init__(self, **kwargs):
        self.id = None
        self.name = None
        self.value = None

        # Initialize after the attributes have been set
        super().__init__(**kwargs)

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and self.value == other.value


class ModelRun(Base):
    """
        Model settings that are used for a particular run

        Attributes:
            - *id:* string
            - *name:* string
            - *description (of how model is being parametrized and run):* string,
            - *model_domain_id:* string
            - *simulation_length:* integer
            - *simulation_length_units:* enum (hours, days, years)
            - *boundary conditions:* Array of :class:`~basin3d.synthesis.models.simulations.MeasurementResults`
    """

    def __init__(self, **kwargs):
        self.id = None
        self.name = None
        self.description = None
        self.model_domain_id = None
        self.simulation_length_units = None  # enum (hours, days, years)
        self.boundary_conditions = []

        # Initialize after the attributes have been set
        super().__init__(**kwargs)

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and self.description == other.description \
                and self.model_domain_id == other.model_domain_id and \
                self.simulation_length_units == other.simulation_length_units


class ModelResults(Base):
    """
        Series of model results

        Attributes:
            - *id:* string
            - *model_run_id:* string
            - *units:* Unit
            - *annotation:* string
            - *result:* Array of :class:`~basin3d.synthesis.models.simulations.ModelDataPoint` objects
    """

    def __init__(self, **kwargs):
        self.id = None
        self.model_run_id = None
        self.units = None
        self.results = []

        # Initialize after the attributes have been set
        super().__init__(**kwargs)

    def __eq__(self, other):
        return self.id == other.id and self.model_run_id == other.model_run_id and self.units == other.units


class ModelDataPoint(Base):  # extends DataPoint
    """
        Class for Model data points get a array of data for each mesh (with different time resolutions)

        Attributes:
            - *id:* string
            - *mesh_id:* string
            - *timestamp:* datetime
            - *value:* float
            - *variable:* :class:`basin3d.models.MeasurementVariable`
    """

    def __init__(self, **kwargs):
        self.id = None
        self.mesh_id = None
        self.timestamp = None
        self.value = None
        self.variable = None

        # Initialize after the attributes have been set
        super().__init__(**kwargs)

    def __eq__(self, other):
        return self.id == other.id and self.mesh_id == other.mesh_id and self.timestamp == other.timestamp \
               and self.value == other.value and self.variable == other.variable


