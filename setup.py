import os
from setuptools import setup, find_packages


NAME = 'huegely'
PACKAGES = find_packages()
DESCRIPTION = 'Python Philips Hue Library'
URL = "https://github.com/kirberich/huegely"
LONG_DESCRIPTION = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
AUTHOR = 'Robert Kirberich'


setup(
    name=NAME,
    version='0.1.0',
    packages=PACKAGES,

    # metadata for upload to PyPI
    author=AUTHOR,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords=["Philips Hue"],
    url=URL,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],

    install_requires=['requests'],
    include_package_data=True,
)
