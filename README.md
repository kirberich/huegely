# Huegely
Huegely is a simple python library to control Philips Hue lights. It mirrors data from the hue bridge transparently, not attempting to do any caching, keeping of state, or similar. 

This is a basic first release, there are no meaningful tests and the API might change drastically. That being said, all the light functionality works.

## Acknowledgements 
Huegely is heavily inspired by https://github.com/studioimaginaire/phue.

## Installation
To install, run `pip install git+https://github.com/kirberich/huegely.git`. 

## Testing
To be able to run the tests (once there any), do the following:

 - Create a python 3 virtualenv called env
 - Run `pip install -r test_requirements.txt`

Using tox:
 - Run `tox`

Running tests directly:
 - Run `py.test`

## Requirements
Huegely requires python 3.x, for no good reason other than that I'm heartless.

The only other requirements is the `requests` library.

## Documentation
Documentation can be found at https://huegely.readthedocs.org/

