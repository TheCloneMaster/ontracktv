# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models, _, Command
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, get_lang


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    amount_total_company_currency = fields.Monetary(
        string='Total en Moneda de Compañía',
        compute='_compute_amount_total_company_currency',
        currency_field='company_currency_id',
        store=True,
    )

    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Moneda de la Compañía',
        readonly=True,
    )

    @api.depends('amount_total', 'currency_id', 'company_id', 'date_order')
    def _compute_amount_total_company_currency(self):
        for order in self:
            if order.currency_id and order.company_id and order.date_order:
                order.amount_total_company_currency = order.currency_id._convert(
                    order.amount_total,
                    order.company_id.currency_id,
                    order.company_id,
                    order.date_order
                )
            else:
                order.amount_total_company_currency = order.amount_total

    def button_approve(self):
        template = self.env.ref('purchase.email_template_edi_purchase_done')
        for po in self:
            template.send_mail(po.id)
        res = super(PurchaseOrder, self.with_context(skip_alternative_check=True)).button_approve()
        return res

    def button_confirm(self):
        if self.alternative_po_ids and not self.env.context.get('skip_alternative_check', False):
            alternative_po_ids = self.alternative_po_ids.filtered(lambda po: po.state in ['draft', 'sent', 'to approve'] and po.id not in self.ids)
            _logger.error('TVCR -Cancelando órdenes de compra alternativas: %s para PO %s', alternative_po_ids.ids, self.id)
            alternative_po_ids.button_cancel()

        _logger.error('TVCR -antes de confirmar')
        res = super(PurchaseOrder, self.with_context(skip_alternative_check=True)).button_confirm()
        _logger.error('TVCR -despues de confirmar')
        if self.need_validation:
            return self.request_validation()
        return res

    def _approval_allowed(self):
        """Returns whether the order qualifies to be approved by the current user"""
        self.ensure_one()
        return not self.need_validation and super()._approval_allowed()
