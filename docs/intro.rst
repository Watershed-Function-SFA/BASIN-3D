.. _basin3dintro:

What is BASIN-3D?
*****************
**Broker for Assimilation, Synthesis and Integration of eNvironmental Diverse, Distributed Datasets**

Earth science research requires integration and analysis of diverse and complex data. Observations
can include continuous sensor-based time-series data, sample-based laboratory characterizations,
remote sensing measurements and derived products, and outputs from numerical simulations. Observations
can span multiple scientific disciplines, as well as disparate spatial and temporal scales. Synthesizing
diverse observations requires substantial resources from scientists because data are often held in multiple
repositories using different formats (e.g. variable names, units, associated metadata), and may be updated over time.

A data broker is a centralized software that aggregates data from connected data sources in
real-time. So far, implementations of data brokering approaches for the earth sciences have only
aggregated catalogs of data sources or integrated observations with the cooperation of data providers.

BASIN-3D (Broker for Assimilation, Synthesis and Integration of eNvironmental Diverse, Distributed Datasets)
is a data brokering framework designed to alleviate earth scientist's data synthesis burden by parsing,
translating, and synthesizing diverse observations from well-curated repositories into a standardized format,
without establishing working relationships with each data source \cite{BASIN-3D}.

BASIN-3D is designed to provide unified access to a diverse set of data sources and data types by connecting
to those data sources in real-time and transforming the data streams to provide an integrated view.
BASIN-3D enables users to always have access to the latest data from each of the sources, but to
deal with the data as if all of the data were integrated in local storage. Our approach to the
brokering architecture is driven by user needs, and is consistent with other recent brokering services
being developed by GEOSS and Earthcube [Jodha Khalsa et al., 2013; Nativi et al., 2013, 2015].

BASIN-3D Django framework connects to distributed data sources via web services,
which enables dynamic retrieval of data and universal access by any client that is authorized to
connect to a BASIN-3D service. Data sources that previously have web-services enabled can
directly plug into the brokering service. Data that are not accessible via web-services can create a
data source web service API for connection with the BASIN-3D.
Some data may need to pass QA/QC inspection and be potentially transformed (e.g. gap-filled) before they are
ready to be used. A federated database enables tracking of all transformations to the data.

Data requests from clients (e.g. a web portal) are made through a REST api. The request is handled by a data
acquisition layer in the broker, which maintains an inventory of the data present in various sources as well as
various simulation codes connected to the broker, and dynamically retrieves data on demand from the appropriate
source (or executes a simulation code if needed). Thereon, data sources’ terminologies are converted to an
abstract, controlled vocabulary maintained by the broker in a data fusion layer.  Similar data are grouped and
transformed into generalized objects with uniform formats defined for each category. For example, different
types of sensor and point time-series data (e.g. meteorological, geochemical time-series) are converted into
uniform time-series objects that a web portal can use to plot in a generic time-series chart, without
knowledge of the type of time-series being represented. Finally a web service layer serves data to clients,
and provides a means for clients to request data and for data providers to be notified if they want to
track their data usage.