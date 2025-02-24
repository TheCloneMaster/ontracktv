# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

import json
from odoo import models, fields, api, _
from odoo.tools.misc import formatLang
from odoo.addons.ekika_utils.tools.helpers import calculate_discount_percentage_per_quantity, calculate_fixed_discount


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    discount = fields.Float(digits='Fix Discount')
    advance_discount = fields.Float(string='Discount', digits='Discount')
    discount_conf_domain = fields.Char('Discount Conf Domain', compute='_compute_discount_conf_domain',
                        default=lambda self: self._make_default_discount_domain())
    discount_conf_id = fields.Many2one('advance.discount.selection', string='Discount Type',
                        domain="discount_conf_domain", default=lambda self: self.env.ref('invoice_discount_per_line.advance_discount_selection_percentage', raise_if_not_found=False))

    def _make_default_discount_domain(self):
        domain_ids = self._get_discount_selection_domain()
        return json.dumps([('id', 'in', domain_ids)])

    def _compute_discount_conf_domain(self):
        for rec in self:
            domain_ids = rec._get_discount_selection_domain()
            rec.discount_conf_domain = json.dumps([('id', 'in', domain_ids)])

    def _get_discount_selection_domain(self):
        domain_ids = []
        if self.env.company.advance_percentage_discount:
            sel = self.env.ref('invoice_discount_per_line.advance_discount_selection_percentage')
            domain_ids.append(sel.id)
        if self.env.company.fix_discount_per_line:
            sel = self.env.ref('invoice_discount_per_line.advance_discount_selection_fix_per_line')
            domain_ids.append(sel.id)
        if self.env.company.fix_discount_per_unit:
            sel = self.env.ref('invoice_discount_per_line.advance_discount_selection_fix_per_unit')
            domain_ids.append(sel.id)
        return domain_ids

    @api.depends('quantity', 'discount', 'advance_discount', 'price_unit', 'tax_ids', 'currency_id')
    def _compute_totals(self):
        for line in self:
            if line.discount_conf_id:
                if line.quantity > 0 and line.price_unit > 0:
                    if line.discount_conf_id.value == 'fix_discount_per_line':
                        line.discount = calculate_discount_percentage_per_quantity(line.quantity, line.price_unit, line.advance_discount)
                    elif line.discount_conf_id.value == 'fix_discount_per_unit':
                        fix_discount_per_line = line.advance_discount * line.quantity
                        line.discount = calculate_discount_percentage_per_quantity(line.quantity, line.price_unit, fix_discount_per_line)
                    elif line.discount_conf_id.value == 'percentage_discount':
                        line.discount = line.advance_discount
        super()._compute_totals()

    @api.depends('tax_ids', 'currency_id', 'partner_id', 'analytic_distribution', 'balance', 'partner_id', 'move_id.partner_id', 'price_unit', 'quantity')
    def _compute_all_tax(self):
        for line in self:
            if line.discount_conf_id:
                if line.quantity > 0 and line.price_unit > 0:
                    if line.discount_conf_id.value == 'fix_discount_per_line':
                        line.discount = calculate_discount_percentage_per_quantity(line.quantity, line.price_unit, line.advance_discount)
                    elif line.discount_conf_id.value == 'fix_discount_per_unit':
                        fix_discount_per_line = line.advance_discount * line.quantity
                        line.discount = calculate_discount_percentage_per_quantity(line.quantity, line.price_unit, fix_discount_per_line)
                    elif line.discount_conf_id.value == 'percentage_discount':
                        line.discount = line.advance_discount
        super()._compute_all_tax()

    def _convert_to_tax_base_line_dict(self):
        res = super()._convert_to_tax_base_line_dict()
        is_invoice = self.move_id.is_invoice(include_receipts=True)
        res['advance_discount'] = self.advance_discount if is_invoice else 0.0
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    fixed_discounts = fields.Monetary(string='Total Discount', compute='_compute_fixed_discounts', store=True)

    @api.depends('line_ids.advance_discount', 'line_ids.discount_conf_id', 'line_ids.quantity', 'line_ids.price_unit')
    def _compute_fixed_discounts(self):
        for move in self:
            move_lines = move.line_ids
            fixed_discounts_lines = 0
            for line in move_lines:
                if line.discount_conf_id:
                    if line.discount_conf_id.value == 'fix_discount_per_line':
                        fixed_discounts_lines += line.advance_discount
                    elif line.discount_conf_id.value == 'fix_discount_per_unit':
                        fixed_discounts_lines += line.advance_discount * line.quantity
                    elif line.discount_conf_id.value == 'percentage_discount':
                        fixed_discounts_lines += calculate_fixed_discount(line.quantity, line.price_unit, line.advance_discount)
            move.fixed_discounts = fixed_discounts_lines

    @api.depends_context('lang')
    @api.depends(
        'invoice_line_ids.currency_rate', 'invoice_line_ids.tax_base_amount', 'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total', 'invoice_line_ids.price_subtotal', 'invoice_payment_term_id',
        'partner_id', 'currency_id',
    )
    def _compute_tax_totals(self):
        super()._compute_tax_totals()
        for rec in self:
            if rec.tax_totals:
                tax_totals = rec.tax_totals
                tax_totals.update({'total_discount': formatLang(self.env, rec.fixed_discounts, currency_obj=rec.currency_id or rec.journal_id.currency_id or rec.company_id.currency_id)})
                rec.tax_totals = tax_totals
