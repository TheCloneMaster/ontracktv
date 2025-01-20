# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero

class StockLandedCostLine(models.Model):
    _inherit = "stock.landed.cost.lines"

    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Provider', readonly=True)
    original_currency_id = fields.Many2one('res.currency', string='Original Currency', readonly=True)
    currency_amount = fields.Monetary(string="Original Amount", required=True, currency_field='original_currency_id')

class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    vendor_bill_ids = fields.Many2many(
        'account.move', string='Vendor Bills', copy=False, domain=[('move_type', '=', 'in_invoice')])


    def _get_targeted_move_ids(self):
        return self.picking_ids.move_ids

    def get_valuation_lines(self):
        self.ensure_one()
        lines = []

        for move in self._get_targeted_move_ids():
            # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
            if move.product_id.cost_method not in ('fifo', 'average') or move.state == 'cancel' or not move.quantity:
                continue
            qty = move.product_uom._compute_quantity(move.quantity, move.product_id.uom_id)
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': qty,
                'former_cost': sum(move.stock_valuation_layer_ids.mapped('value')),
                'weight': move.product_id.weight * qty,
                'volume': move.product_id.volume * qty
            }
            lines.append(vals)

        if not lines:
            target_model_descriptions = dict(self._fields['target_model']._description_selection(self.env))
            raise UserError(_("You cannot apply landed costs on the chosen %s(s). Landed costs can only be applied for products with FIFO or average costing method.", target_model_descriptions[self.target_model]))
        return lines

    def reconcile_landed_cost(self):
        for cost in self:
            for bill in cost.vendor_bill_ids:
                if bill.state == 'posted' and cost.company_id.anglo_saxon_accounting:
                    all_amls = bill.line_ids | cost.account_move_id.line_ids
                    for product in cost.cost_lines.product_id:
                        accounts = product.product_tmpl_id.get_product_accounts()
                        input_account = accounts['stock_input']
                        all_amls.filtered(lambda aml: aml.account_id == input_account and not aml.reconciled\
                            and not aml.display_type in ('line_section', 'line_note')).reconcile()

