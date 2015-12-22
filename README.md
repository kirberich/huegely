# Huegely [![Build Status](https://travis-ci.org/kirberich/huegely.svg?branch=master)](https://travis-ci.org/kirberich/huegely) [![codecov.io](https://codecov.io/github/kirberich/huegely/coverage.svg?branch=master)](https://codecov.io/github/kirberich/huegely?branch=master)
Huegely is a simple python library to control Philips Hue lights. It mirrors data from the hue bridge transparently, not attempting to do any caching, keeping of state, or similar.

### Features
 - All hue light features should be supported (at least for the standard lights, I don't have any of the the more exotic ones to try)
 - The full group API is supported, allowing querying for, getting state from and applying actions to, groups.

### What huegely doesn't do (but might at some point)
 - Using RGB for colours.
 - Return meaningful state for groups (would have to be some kind of average of lamp states).
 - Have some functional tests, not just feel-good coverage.

### What huegely probably never will do (or at least I likely won't add it)
 - Searching for / adding new lights/groups/rules/schedules (as I don't have any need for it, the app works fine for that).
 - Having a command line interface.
 - Having some kind of server (it's written to be used by apps and servers and things, not to be one).

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

