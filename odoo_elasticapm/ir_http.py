# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import elastic_apm_client, elasticapm, odoo_version

try:
    from odoo.addons.base.ir.ir_http import IrHttp
    from odoo.http import request
except ImportError:
    from openerp.addons.base.ir.ir_http import ir_http as IrHttp
    from openerp.http import request

SKIP_PATH = [
    "/connector/runjob",
    "/longpolling/",
    ]


def get_data_from_request(request):
    httprequest = request.httprequest
    data = {
        "headers": dict(**httprequest.headers),
        "method": httprequest.method,
        "socket": {
            "remote_address": httprequest.remote_addr,
            "encrypted": httprequest.scheme == 'https'
        },
        "url": elasticapm.utils.get_url_dict(httprequest.url)
    }
    # remove Cookie header since the same data is in request["cookies"] as well
    data["headers"].pop("Cookie", None)
    return data


def get_data_from_response(response):
    return {"status_code": response.status_code}


ori_dispatch = IrHttp._dispatch


def _dispatch(self):
    path_info = request.httprequest.environ.get('PATH_INFO')
    for path in SKIP_PATH:
        if path_info.startswith(path):
            return ori_dispatch(self)

    name = path_info
    for key in ['model', 'method', 'signal']:
        val = request.params.get(key)
        if val and val not in name:
            name += ' {}: {}'.format(key, val)

    elastic_apm_client.begin_transaction('request')
    response = ori_dispatch(self)
    elasticapm.set_context(lambda: get_data_from_request(request), "request")
    elasticapm.set_context(lambda: get_data_from_response(response), "response")
    elastic_apm_client.end_transaction(name, response.status_code)
    return response


IrHttp._dispatch = _dispatch
