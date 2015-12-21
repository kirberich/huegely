from huegely import constants


def parse_attribute_from_url(resource_url):
    """ Returns the original attribute from the resource url contained in API responses.
        This is simply the last element in a resource url as returned by the API.

        API responses look like {'success': {'resource_url': resource_value}},
        with, for example, a url such as '/lights/<id>/state/bri' for the brightness attribute.
    """
    return resource_url.rsplit('/', 1)[-1]


def huegely_to_hue_names(attributes):
    """ Maps attributes to their hue API names, e.g. 'brightness' becomes 'bri'. """
    return {
        constants.HUEGELY_TO_HUE_MAPPING.setdefault(key, key): value for key, value in attributes.items()
    }


def hue_to_huegely_names(attributes):
    """ Maps attributes to their huegely names, e.g. 'bri' becomes 'brightness'. """
    return {
        constants.HUE_TO_HUEGELY_MAPPING.setdefault(key, key): value for key, value in attributes.items()
    }
