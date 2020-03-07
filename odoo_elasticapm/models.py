# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .base import elasticapm

try:
    from odoo import api, models
except ImportError:
    from openerp import api, models


def build_params(self, method):
    return {
        'name': "ORM %s %s" % (self._name, method),
        'span_type': 'odoo',
        'span_subtype': 'orm',
        'extra': {
            'odoo': {
                'class': self._name,
                'method': method,
                'nbr_record': hasattr(self, '_ids') and len(self) or 0,
                }
            }
        }


Model = models.Model
ori_create = Model.create
ori_write = Model.write
ori_search = Model._search
ori_unlink = Model.unlink


@api.model
def create(self, vals):
    with elasticapm.capture_span(**build_params(self, "create")):
        return ori_create(self, vals)


@api.multi
def write(self, vals):
    with elasticapm.capture_span(**build_params(self, "write")):
        return ori_write(self, vals)


def unlink(self, cr, uid, ids, context=None):
    with elasticapm.capture_span(**build_params(self, "unlink")):
        return ori_unlink(self, cr, uid, ids, context=context)


def _search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False, access_rights_uid=None):
    with elasticapm.capture_span(**build_params(self, "search")):
        return ori_search(self, cr, uid, args, offset=offset, limit=limit, order=order,
                   context=context, count=count, access_rights_uid=access_rights_uid)


Model.create = create
Model.write = write
Model._search = _search
Model.unlink = unlink
