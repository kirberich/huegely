*******
Huegely
*******

Huegely is a simple python library to control Philips Hue lights. It mirrors data from the hue bridge transparently, not attempting to do any caching, keeping of state, or similar.

It is meant to be used as a consistent and reliable direct representation of the state of the hue bridge. Any apps that use it will likely want to add some caching and watch how many API requests they make. Philips recommends staying below 10 commands per second for lights and 1 request per second for groups. You might be able to get away with more, but your mileage may vary.

Most huegely commands use a single API request, but some use two.

.. toctree::
   :maxdepth: 3
   :caption: Contents

   basic_usage
   transition_times
   bridge_api
   light_api
   group_api
   exceptions
