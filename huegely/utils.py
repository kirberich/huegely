def parse_attribute_from_url(resource_url):
    """ Returns the original attribute from the resource url contained in API responses.
        This is simply the last element in a resource url as returned by the API.

        API responses look like {'success': {'resource_url': resource_value}},
        with, for example, a url such as '/lights/<id>/state/bri' for the brightness attribute.
    """
    return resource_url.rsplit('/', 1)[-1]