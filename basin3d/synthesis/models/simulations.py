"""


`basin3d.synthesis.models.simulations`
**************************************

.. currentmodule:: basin3d.synthesis.models.simulations

:synopsis: Classes to represent Simulation/Modeling Concepts


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
            - *web_location:* string
            - *dimensionality:* enum (1D, 2D, 3D)
    """

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.name = None
        self.version = None
        self.web_location = None
        self.dimensionality = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

    def __eq__(self, other):
        return self.id == other.id and self.version == other.version \
               and self.web_location == other.web_location and self.dimensionality == other.dimensionality


class ModelDomain(Base):
    """
        Specifies the area being modeled

        Attributes:
            - *id:* string
            - *name:* string
            - *geom:* Polygon
            - has one ore more :class:`~basin3d.synthesis.models.simulations.Mesh` objects as **meshes**
    """

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.name = None
        self.geom = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

    def __eq__(self, other):
        return self.id == other.model_domain_id and self.name == other.model_domain_name \
               and self.geom == other.geom


class Mesh(Base):
    """
        A sub-area within the model domain

        Attributes:
            - *mesh_id:* string
            - *parameters:* Array of :class:`~basin3d.synthesis.models.simulations.ModelParameter` objects
            - *initial_conditions:* Array of :class:`basin3d.models.MeasurementVariable` objects
            - *geom:* Polygon
    """

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.parameters = []
        self.initial_conditions = []
        self.geom = {}

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

    def __eq__(self, other):
        return self.id == other.mesh_id


class ModelParameter(Base):
    """
        Parameters set in the equation the model is solving.

        Attributes:
            - *id:* string
            - *model_name:* string (the parameter name in the :class:`~basin3d.synthesis.models.simulations.Model`)
            - *data_source_name:* string (the parameter name in the :class:`basin3d.models.DataSource`)
            - *value:* float
    """

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.model_name = None
        self.data_source_name = None
        self.value = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

    def __eq__(self, other):
        return self.id == other.id and self.model_name == other.model_name and self.value == other.value


class ModelRun(Base):
    """
        Model settings that are used for a particular run

        Attributes:
            - *id:* string -- the model run number
            - *name:* string
            - *start_time*: datetime -- system time when simulation started
            - *end_time:* datetime -- system time when results obtained
            - *simulation_length:* integer
            - *simulation_length_units:* enum (hours, days, years)
            - *status*: enum -- (started, finished, delayed,canceled)
            - has one or more :class:`~basin3d.synthesis.models.simulations.MeasurementResults` as **boundary_conditions**
            - has a :class:`~basin3d.synthesis.models.simulations.ModelDomain` as **model_domain**



    """

    STATUS_QUEUED="Queued"
    STATUS_STARTED="Running"
    STATUS_DONE="Done"

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.name = None
        self.start_time = None
        self.end_time = None
        self.simulation_length = None
        self.simulation_length_units = None  # enum (hours, days, years)
        self.status = self.STATUS_QUEUED

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

        if self.start_time:
            if self.end_time:
                self.status = self.STATUS_DONE
            else:
                self.status = self.STATUS_STARTED

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name \
               and self.id == other.id and \
               self.simulation_length_units == other.simulation_length_units


class ModelResults(Base):
    """
        Series of model results

        Attributes:
            - *id:* string
            - *units:* Unit
            - *annotation:* string
            - has one or more  :class:`~basin3d.synthesis.models.simulations.ModelDataPoint` objects as **result**
            - has a :class:`~basin3d.synthesis.models.simulations.ModelRun` as **model_run**
    """

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.units = None
        self.annotation = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

    def __eq__(self, other):
        return self.id == other.id and self.units == other.units


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

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.mesh_id = None
        self.timestamp = None
        self.value = None
        self.variable = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

    def __eq__(self, other):
        return self.id == other.id and self.mesh_id == other.mesh_id and self.timestamp == other.timestamp \
               and self.value == other.value and self.variable == other.variable


