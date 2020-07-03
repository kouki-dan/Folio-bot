
from setuptools import setup, find_packages
import version


setup(
    name="Folio bot",
    version=version.version,
    packages=find_packages(),
    test_suite="test",
    install_requires=[
        "flask",
        "mechanicalsoup",
    ],
)
