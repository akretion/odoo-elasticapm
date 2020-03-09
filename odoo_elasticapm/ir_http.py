# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import elastic_apm_client, elasticapm, version_older_then
from .http import get_data_from_request

try:
    from odoo.addons.base.models.ir_http import IrHttp
    from odoo.http import request
except ImportError:
    try:
        from odoo.addons.base.ir.ir_http import IrHttp
        from odoo.http import request
    except ImportError:
        from openerp.addons.base.ir.ir_http import ir_http as IrHttp
        from openerp.http import request

SKIP_PATH = ["/connector/runjob", "/longpolling/"]


def get_data_from_response(response):
    return {"status_code": response.status_code}


ori_dispatch = IrHttp._dispatch


def skip_tracing():
    path_info = request.httprequest.environ.get("PATH_INFO")
    for path in SKIP_PATH:
        if path_info.startswith(path):
            return True
    return False


def before_dispatch():
    elastic_apm_client.begin_transaction("request")
    elasticapm.set_user_context(user_id=request.session.uid)


def after_dispatch(response):
    path_info = request.httprequest.environ.get("PATH_INFO")
    name = path_info
    for key in ["model", "method", "signal"]:
        val = request.params.get(key)
        if val and val not in name:
            name += " {}: {}".format(key, val)
    elasticapm.set_context(lambda: get_data_from_request(), "request")
    elasticapm.set_context(lambda: get_data_from_response(response), "response")
    elastic_apm_client.end_transaction(name, response.status_code)


if version_older_then("10.0"):

    def _dispatch(self):
        if skip_tracing():
            return ori_dispatch(self)
        else:
            before_dispatch()
            response = ori_dispatch(self)
            after_dispatch(response)
            return response


else:

    @classmethod
    def _dispatch(cls):
        if skip_tracing():
            return ori_dispatch()
        else:
            before_dispatch()
            response = ori_dispatch()
            after_dispatch(response)
            return response


IrHttp._dispatch = _dispatch
