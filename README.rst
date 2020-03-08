odoo-elasticapm
=================

.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. image:: https://badge.fury.io/py/odoo-elasticapm.svg
    :target: http://badge.fury.io/py/odoo-elasticapm

odoo-elasticapm integrate the APM tracking from the ELK suite

.. contents::

Quick start
~~~~~~~~~~~

Install ``odoo-elasticapm``::

  pip install odoo-elasticapm


Then instead of launching odoo with ``odoo`` cmd use ``odoo-elasticapm``::

  odoo-elasticapm


Configuration

Following environment variable are needed:

ELASTIC_APM_SERVER_URL=http://apm-server:8200


The following one are optionnal:

ELASTIC_APM_SERVICE_NAME=my-customer
ELASTIC_APM_TRANSACTION_SAMPLE_RATE=0.1

All environment variable are available on official documentation:
https://www.elastic.co/guide/en/apm/agent/python/current/configuration.html
