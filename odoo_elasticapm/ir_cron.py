# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import elastic_apm_client, elasticapm, version_older_then

try:
    from odoo.addons.base.models.ir_cron import ir_cron as IrCron
except ImportError:
    try:
        from odoo.addons.base.ir.ir_cron import ir_cron as IrCron
        from odoo import api
    except ImportError:
        from openerp.addons.base.ir.ir_cron import ir_cron as IrCron
        from openerp import api


def before_cron(job):
    elastic_apm_client.begin_transaction("cron")
    elasticapm.set_user_context(user_id=job["user_id"])


def after_cron(job):
    if "name" in job:
        name = job["name"]
    else:
        name = job["cron_name"]
    elastic_apm_client.end_transaction(name)


ori_process_job = IrCron._process_job


if version_older_then("10.0"):

    def _process_job(self, job_cr, job, cron_cr):
        before_cron(job)
        ori_process_job(self, job_cr, job, cron_cr)
        after_cron(job)


else:

    @classmethod
    def _process_job(cls, job_cr, job, cron_cr):
        before_cron(job)
        ori_process_job(job_cr, job, cron_cr)
        after_cron(job)


IrCron._process_job = _process_job

ori_handle_callback_exception = IrCron._handle_callback_exception


def capture_exception(name, job_exception):
    elasticapm.label(
        exception_source="cron",
        exception_cron=name,
        exception_type=type(job_exception).__name__,
        exception_handled=False,
    )
    elastic_apm_client.capture_exception(handled=False)


if version_older_then("10.0"):

    def _handle_callback_exception(
        self, cr, uid, model_name, method_name, args, job_id, job_exception
    ):
        ori_handle_callback_exception(
            self, cr, uid, model_name, method_name, args, job_id, job_exception
        )
        job = self.browse(cr, uid, job_id)
        capture_exception(job.name, job_exception)


elif version_older_then("11.0"):

    @api.model
    def _handle_callback_exception(
        self, model_name, method_name, args, job_id, job_exception
    ):
        ori_handle_callback_exception(
            self, model_name, method_name, args, job_id, job_exception
        )
        job = self.browse(job_id)
        capture_exception(job.name, job_exception)


else:

    @api.model
    def _handle_callback_exception(
        self, cron_name, server_action_id, job_id, job_exception
    ):
        ori_handle_callback_exception(
            self, cron_name, server_action_id, job_id, job_exception
        )
        job = self.browse(job_id)
        capture_exception(job.name, job_exception)


IrCron._handle_callback_exception = _handle_callback_exception
