QUERY_PARAM_MONITORING_FEATURES = "monitoring_features"
QUERY_PARAM_OBSERVED_PROPERTY_VARIABLES = "observed_property_variables"
QUERY_PARAM_AGGREGATION_DURATION = "aggregation_duration"
QUERY_PARAM_START_DATE = "start_date"
QUERY_PARAM_END_DATE = "end_date"
QUERY_PARAM_SUBBASINS = "subbasins"
QUERY_PARAM_REGIONS = "regions"
QUERY_PARAM_RESULT_QUALITY = "result_quality"


def extract_id(identifer):
    """
    Extract the datasource identifier from the broker identifier

    :param identifer:
    :return:
    """
    if identifer:
        site_list = identifer.split("-")
        identifer = identifer.replace("{}-".format(site_list[0]),
                                      "", 1)  # The datasource id prefix needs to be removed
    return identifer


def filter_query_param_values(request, param_name, id_prefix, query_params):
    """
    Filter query param values for those with the specified id_prefix

    :param request:
    :param param_name:
    :param id_prefix:
    :param query_params:
    :return:
    """
    # Synthesize the ids (remove datasource id_prefix)
    if param_name in request.query_params:
        values = request.query_params.get(param_name, None)

        if values:
            query_params[param_name] = [x for x in
                                        values.split(",")
                                        if x.startswith("{}-".format(id_prefix))]


def extract_query_param_ids(request, param_name, id_prefix, query_params):
    """
    Extract the ids from the specified query params

    :param request: This original request
    :param param_name: the name of the list parameter
    :param id_prefix:  the datasource id prefix
    :param query_params: the query params to populate
    :type query_params: dict
    :return:
    """
    # Synthesize the ids (remove datasource id_prefix)
    if param_name in request.query_params:
        values = request.query_params.get(param_name, None)

        if values:
            query_params[param_name] = [extract_id(x) for x in
                                        values.split(",")
                                        if x.startswith("{}-".format(id_prefix))]