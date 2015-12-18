**********
Exceptions
**********

A HueError is raised whenever an API request fails. As it contains the error code, high-level functions can use this to distinguish expected from unexpected errors. For example, Light.darker() will receive a HueError if the light is already off, which can be safely ignored and is hence swallowed.

.. autoclass:: huegely.exceptions.HueError
    :members:
    :undoc-members:
    :inherited-members: