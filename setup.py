"""Sphinx Bootstrap Theme package."""
import codecs
import os
from io import open as io_open

from setuptools import setup


# loosely from https://packaging.python.org/guides/single-sourcing-package-version/
HERE = os.path.abspath(os.path.dirname(__file__))

__version__ = None
version_file = os.path.join(HERE, 'pyansys_sphinx_theme', '_version.py')
with io_open(version_file, mode='r') as fd:
    exec(fd.read())


def read(rel_path):
    with codecs.open(os.path.join(HERE, rel_path), 'r') as fp:
        return fp.read()


# Get the long description from the README file
with open(os.path.join(HERE, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="pyansys-sphinx-theme",
    version=__version__,
    description="PyData-based Sphinx theme from the PyAnsys community",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/pyansys/pyansys-sphinx-theme",
    license="MIT",
    maintainer="Alexander Kaszynski",
    maintainer_email="alexander.kaszynski@ansys.com",
    #
    packages=["pyansys_sphinx_theme"],
    include_package_data=True,
    # See http://www.sphinx-doc.org/en/stable/theming.html#distribute-your-theme-as-a-python-package
    entry_points={"sphinx.html_themes": ["pyansys_sphinx_theme = pyansys_sphinx_theme"]},
    install_requires=["sphinx",
                      "pydata-sphinx-theme==0.6.3",
                      ],
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Framework :: Sphinx",
        "Framework :: Sphinx :: Theme",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
