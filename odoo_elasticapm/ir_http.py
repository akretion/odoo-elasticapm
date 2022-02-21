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

SKIP_PATH = ["/connector/runjob", "/longpolling/", "/web_editor"]

def base_dispatch(cls):
    cls._handle_debug()

    # locate the controller method
    try:
        rule, arguments = cls._match(request.httprequest.path)
        func = rule.endpoint
    except werkzeug.exceptions.NotFound as e:
        return cls._handle_exception(e)

    # check authentication level
    try:
        auth_method = cls._authenticate(func)
    except Exception as e:
        return cls._handle_exception(e)

    processing = cls._postprocess_args(arguments, rule)
    if processing:
        return processing

    # set and execute handler
    try:
        request.set_handler(func, arguments, auth_method)
        result = request.dispatch()
        if isinstance(result, Exception):
            raise result
    except Exception as e:
        return cls._handle_exception(e)

    return result

ori_dispatch = base_dispatch


def skip_tracing():
    path_info = request.httprequest.environ.get("PATH_INFO")
    for path in SKIP_PATH:
        if path_info.startswith(path):
            return True
    return False


def before_dispatch():
    print("\n\n\n Called in before_dispatch \n\n\n")
    elastic_apm_client.begin_transaction("request")
    elasticapm.set_user_context(user_id=request.session.uid)


def after_dispatch(response):
    print("\n\n\n Called in after_dispatch \n\n\n")
    path_info = request.httprequest.environ.get("PATH_INFO")
    name = path_info
    for key in ["model", "method", "signal"]:
        val = request.params.get(key)
        if val and val not in name:
            name += " {}: {}".format(key, val)
    elasticapm.set_context(lambda: get_data_from_request(), "request")
    try:
        code = response.status_code
    except Exception:
        try:
            code = response.code
        except Exception:
            code = "NoCodeFound"
    elastic_apm_client.end_transaction(name, code)


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
            return ori_dispatch(cls)
        else:
            before_dispatch()
            response = ori_dispatch(cls)
            after_dispatch(response)
            return response


IrHttp._dispatch = _dispatch

