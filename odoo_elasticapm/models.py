# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .base import elasticapm, version_older_then

try:
    from odoo import api, models
except ImportError:
    from openerp import api, models


def build_params(self, method):
    return {
        "name": "ORM {} {}".format(self._name, method),
        "span_type": "odoo",
        "span_subtype": "orm",
        "extra": {
            "odoo": {
                "class": self._name,
                "method": method,
                "nbr_record": hasattr(self, "_ids") and len(self) or 0,
            }
        },
    }


Model = models.Model
ori_create = Model.create
ori_write = Model.write
ori_search = Model._search
ori_unlink = Model.unlink


def write(self, vals):
    with elasticapm.capture_span(**build_params(self, "write")):
        return ori_write(self, vals)


@api.returns("self", lambda value: value.id)
def create(self, vals):
    with elasticapm.capture_span(**build_params(self, "create")):
        return ori_create(self, vals)


def _search(self, *args, **kwargs):
    with elasticapm.capture_span(**build_params(self, "search")):
        return ori_search(self, *args, **kwargs)


def unlink(self):
    with elasticapm.capture_span(**build_params(self, "unlink")):
        return ori_unlink(self)


if version_older_then("13.0"):
    unlink = api.multi(unlink)
    write = api.multi(write)

if version_older_then("12.0"):
    create = api.model(create)
else:
    create = api.model_create_multi(create)


if version_older_then("10.0"):
    _search = api.cr_uid_context(_search)
else:
    _search = api.model(_search)

Model.create = create
Model.write = write
Model._search = _search
Model.unlink = unlink
