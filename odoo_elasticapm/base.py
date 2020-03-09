# -*- coding: utf-8 -*-


import os

import elasticapm

try:
    from odoo.tools.config import config
    import odoo
except ImportError:
    from openerp.tools.config import config
    import openerp as odoo

odoo_version = odoo.release.version


def version_older_then(version):
    return (
        odoo.tools.parse_version(odoo_version)[0] < odoo.tools.parse_version(version)[0]
    )


if os.environ.get("ELASTIC_APM_ENVIRONMENT"):
    environment = os.environ.get("ELASTIC_APM_ENVIRONMENT")
else:
    environment = config.get("running_env")

elasticapm.instrument()

elastic_apm_client = elasticapm.Client(
    framework_name="Odoo",
    framework_version=odoo_version,
    service_name=os.environ.get("ELASTIC_APM_SERVICE_NAME", "Odoo"),
    environment=environment,
)


# The elasticapm lib will import gevent odoo think that we launch him in gevent mode
# we need to force back to normal mode here
odoo.evented = False
