from rest_framework_swagger import renderers


class JSONOpenAPIRenderer(renderers.OpenAPIRenderer):
    """
    To allow application/json request
    """
    media_type = 'application/json'