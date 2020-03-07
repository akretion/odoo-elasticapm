# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import elastic_apm_client, odoo_version

try:
    from odoo.addons.base.models.ir_cron import ir_cron as IrCron
except ImportError:
    try:
        from odoo.addons.base.ir.ir_cron import ir_cron as IrCron
    except ImportError:
        from openerp.addons.base.ir.ir_cron import ir_cron as IrCron


def before_cron():
    elastic_apm_client.begin_transaction("cron")


def after_cron(job):
    if "name" in job:
        name = job["name"]
    else:
        name = job["cron_name"]
    elastic_apm_client.end_transaction(name)


ori_process_job = IrCron._process_job


if odoo_version in ["8.0", "9.0"]:

    def _process_job(self, job_cr, job, cron_cr):
        before_cron()
        ori_process_job(self, job_cr, job, cron_cr)
        after_cron(job)


else:

    @classmethod
    def _process_job(cls, job_cr, job, cron_cr):
        before_cron()
        ori_process_job(job_cr, job, cron_cr)
        after_cron(job)


IrCron._process_job = _process_job
