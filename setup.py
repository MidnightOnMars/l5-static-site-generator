#!/usr/bin/env python3
"""
Minimal setup script to install the ``ssg`` package in editable mode.
This allows ``python -m ssg`` to be executed from any working directory,
which is required by the test suite.
"""
from setuptools import setup, find_packages

setup(
    name="ssg",
    version="0.1.0",
    description="A minimal static site generator",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "jinja2",
        "pyyaml",
        "pygments",
        "markdown",
    ],
    entry_points={
        "console_scripts": [
            "ssg=ssg.cli:main",
        ],
    },
)