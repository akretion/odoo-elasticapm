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


@api.multi
def write(self, vals):
    with elasticapm.capture_span(**build_params(self, "write")):
        return ori_write(self, vals)


if version_older_then("11.0"):

    @api.model
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        with elasticapm.capture_span(**build_params(self, "create")):
            return ori_create(self, vals)


else:

    @api.model_create_multi
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        with elasticapm.capture_span(**build_params(self, "create")):
            return ori_create(self, vals)


if version_older_then("10.0"):

    @api.cr_uid_ids_context
    def unlink(self, cr, uid, ids, context=None):
        with elasticapm.capture_span(**build_params(self, "unlink")):
            return ori_unlink(self, cr, uid, ids, context=context)

    @api.cr_uid_context
    def _search(
        self,
        cr,
        uid,
        args,
        offset=0,
        limit=None,
        order=None,
        context=None,
        count=False,
        access_rights_uid=None,
    ):
        with elasticapm.capture_span(**build_params(self, "search")):
            return ori_search(
                self,
                cr,
                uid,
                args,
                offset=offset,
                limit=limit,
                order=order,
                context=context,
                count=count,
                access_rights_uid=access_rights_uid,
            )


else:

    @api.multi
    def unlink(self):
        with elasticapm.capture_span(**build_params(self, "unlink")):
            return ori_unlink(self)

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        with elasticapm.capture_span(**build_params(self, "search")):
            return ori_search(
                self,
                args,
                offset=offset,
                limit=limit,
                order=order,
                count=count,
                access_rights_uid=access_rights_uid,
            )


Model.create = create
Model.write = write
Model._search = _search
Model.unlink = unlink
