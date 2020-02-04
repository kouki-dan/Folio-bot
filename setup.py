
from setuptools import setup, find_packages

setup(
    name="Folio bot",
    version="0.6.0",
    packages=find_packages(),
    test_suite="test",
    install_requires=[
        "mechanicalsoup",
    ],
)

