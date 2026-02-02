"""
Setup configuration for OREI HDMI Matrix integration.

:copyright: (c) 2026 by Custom Integration.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ucapi-orei-hdmi-matrix",
    version="0.1.0",
    author="Custom Integration",
    description="OREI BK-808 HDMI Matrix integration for Unfolded Circle Remote Two/3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/unfoldedcircle",
    packages=find_packages(),
    package_dir={"": "src"},
    py_modules=["src.driver", "src.orei_matrix"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Home Automation",
    ],
    python_requires=">=3.11",
    install_requires=[
        "ucapi>=0.5.0",
        "pyee>=11.0.0",
    ],
    entry_points={
        "console_scripts": [
            "orei-matrix-driver=src.driver:main",
        ],
    },
)
