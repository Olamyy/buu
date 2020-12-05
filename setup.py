import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())


setup(
    name="buu",
    version="0.1.1",
    url="https://github.com/kragniz/cookiecutter-pypackage-minimal",
    license='MIT',

    author="Olamilekan Wahab",
    author_email="olamyy53@gmail.com",

    description="A wrapper around vegeta for load testing sagemaker endpoints",
    long_description=read("README.rst"),

    packages=find_packages(exclude=('tests',)),

    entry_points={
        "console_scripts": [
            "buu = app.main:cli"
        ]
    },

    install_requires=['pyyaml', 'boto3', 'requests', 'click'],

    classifiers=[],
)
