# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import elastic_apm_client, elasticapm

try:
    from odoo.http import WebRequest, request
    from odoo.exceptions import (
        UserError,
        RedirectWarning,
        AccessDenied,
        AccessError,
        MissingError,
        ValidationError,
        except_orm,
    )


except ImportError:
    from openerp.http import WebRequest, request
    from openerp.exceptions import (
        Warning as UserError,
        RedirectWarning,
        AccessDenied,
        AccessError,
        MissingError,
        ValidationError,
        except_orm,
    )

EXCEPTIONS = [
    UserError,
    RedirectWarning,
    AccessDenied,
    AccessError,
    MissingError,
    ValidationError,
    except_orm,
]


def get_data_from_request():
    httprequest = request.httprequest
    data = {
        "headers": dict(**httprequest.headers),
        "method": httprequest.method,
        "socket": {
            "remote_address": httprequest.remote_addr,
            "encrypted": httprequest.scheme == "https",
        },
        "url": elasticapm.utils.get_url_dict(httprequest.url),
    }
    # remove Cookie header since the same data is in request["cookies"] as well
    data["headers"].pop("Cookie", None)
    return data


ori_handle_exception = WebRequest._handle_exception


def _handle_exception(self, exception):
    handled = False
    for exception_class in EXCEPTIONS:
        if isinstance(exception, exception_class):
            handled = True
    elasticapm.label(
        exception_source="request",
        exception_type=type(exception).__name__,
        exception_handled=handled,
    )
    elastic_apm_client.capture_exception(
        context={"request": get_data_from_request()}, handled=handled
    )
    return ori_handle_exception(self, exception)


WebRequest._handle_exception = _handle_exception
