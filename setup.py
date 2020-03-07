# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

long_description = []
with open(os.path.join("README.rst")) as f:
    long_description.append(f.read())
with open(os.path.join("CHANGES.rst")) as f:
    long_description.append(f.read())


setup(
    name="odoo-elasticapm",
    description="Elastic APM integration for Odoo",
    long_description="\n".join(long_description),
    use_scm_version=True,
    packages=["odoo_elasticapm"],
    include_package_data=True,
    setup_requires=["setuptools_scm"],
    install_requires=["elastic-apm>=5.4"],
    license="AGPLv3+",
    author="Akretion",
    author_email="contact@akretion.com",
    url="http://github.com/akretion/odoo-elasticapm",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: "
        "GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Framework :: Odoo",
    ],
    entry_points="""
        [console_scripts]
        odoo-elasticapm=odoo_elasticapm.cli:main
    """,
)
