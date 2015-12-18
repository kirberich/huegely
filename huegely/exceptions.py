LINK_BUTTON_NOT_PRESSED = 101
CANNOT_MODIFY_WHILE_OFF = 201


class HueError(Exception):
    """ Exception for hue api errors, containing the error code
        to allow more specific error handling.
    """
    def __init__(self, message, error_code=None, device=None, *args):
        self.error_code = error_code
        self.device = device

        super(HueError, self).__init__(message, *args)
