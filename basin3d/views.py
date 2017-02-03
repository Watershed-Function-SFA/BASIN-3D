from collections import OrderedDict

from django.core.urlresolvers import NoReverseMatch
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def broker_api_root(request, format=None):

    root_dict = OrderedDict()
    # Iterate over the possible views. If they are enabled add them to the
    # root api.
    for k,v in [('direct-apis','direct-api-list'),('synthesis-regions','region-list'),
                ('synthesis-models','model-list'), ('synthesis-modeldomains','modeldomain-list'),
                ('synthesis-mesh','mesh-list')]:

        try:
            root_dict[k]=reverse(v, request=request, format=format)
        except NoReverseMatch:
            # If there is no match just don't show it
            pass

    return Response(root_dict)