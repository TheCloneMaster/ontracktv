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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount = fields.Float(digits='Fix Discount')
    discount_conf_domain = fields.Char('Discount Conf Domain', compute='_compute_discount_conf_domain',
                        default=lambda self: self._make_default_discount_domain())
    discount_conf_id = fields.Many2one('advance.discount.selection', string='Discount Type',
                        domain="discount_conf_domain", default=lambda self: self.env.ref('invoice_discount_per_line.advance_discount_selection_percentage', raise_if_not_found=False))
    advance_discount = fields.Float(string='Discount', digits='Discount')

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

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'discount_conf_id', 'advance_discount')
    def _compute_discount(self):
        super()._compute_discount()
        for line in self:
            if line.discount_conf_id:
                if line.product_uom_qty > 0 and line.price_unit > 0:
                    if line.discount_conf_id.value == 'fix_discount_per_line':
                        line.discount = calculate_discount_percentage_per_quantity(line.product_uom_qty, line.price_unit, line.advance_discount)
                    elif line.discount_conf_id.value == 'fix_discount_per_unit':
                        fix_discount_per_line = line.advance_discount * line.product_uom_qty
                        line.discount = calculate_discount_percentage_per_quantity(line.product_uom_qty, line.price_unit, fix_discount_per_line)
                    elif line.discount_conf_id.value == 'percentage_discount':
                        line.discount = line.advance_discount

    @api.depends('product_uom_qty', 'discount', 'discount_conf_id', 'advance_discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        super()._compute_amount()

    def _convert_to_tax_base_line_dict(self, **kwargs):
        res = super()._convert_to_tax_base_line_dict(**kwargs)
        res['advance_discount'] = self.advance_discount
        return res

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        if self.discount_conf_id:
            if self.discount_conf_id.value == 'fix_discount_per_line':
                if self.product_id.invoice_policy == 'delivery':
                    target_quantity = self.qty_delivered - self.qty_invoiced
                    res['advance_discount'] = self.calculate_line_delivery_fixed_discount(self.product_uom_qty, self.advance_discount, target_quantity)
                elif self.product_id.invoice_policy == 'order':
                    res['advance_discount'] = self.advance_discount
            elif self.discount_conf_id.value == 'fix_discount_per_unit':
                res['advance_discount'] = self.advance_discount
            elif self.discount_conf_id.value == 'percentage_discount':
                res['advance_discount'] = self.advance_discount
            res['discount_conf_id'] = self.discount_conf_id.id
        return res

    def calculate_line_delivery_fixed_discount(self, base_quantity, base_discount, target_quantity):
        """
        Calculate the discount for a target quantity based on the discount for a base quantity.

        Args:
            base_quantity (int): The quantity for which the discount is known.
            base_discount (float): The discount amount for the base quantity.
            target_quantity (int): The quantity for which the discount needs to be calculated.

        Returns:
            float: The discount for the target quantity.
        """
        if base_quantity == 0:
            raise ValueError("Base quantity cannot be zero.")
        return (base_discount / base_quantity) * target_quantity


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fixed_discounts = fields.Monetary(string='Total Discount', compute='_compute_fixed_discounts', store=True)

    def _prepare_down_payment_section_line(self, **optional_values):
        res = super()._prepare_down_payment_section_line(**optional_values)
        res['discount_conf_id'] = False
        res['advance_discount'] = 0
        return res

    @api.depends('order_line.advance_discount', 'order_line.product_uom_qty', 'order_line.price_unit', 'order_line.discount_conf_id')
    def _compute_fixed_discounts(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            fixed_discounts_lines = 0
            for line in order_lines:
                if line.discount_conf_id:
                    if line.discount_conf_id.value == 'fix_discount_per_line':
                        fixed_discounts_lines += line.advance_discount
                    elif line.discount_conf_id.value == 'fix_discount_per_unit':
                        fixed_discounts_lines += line.advance_discount * line.product_uom_qty
                    elif line.discount_conf_id.value == 'percentage_discount':
                        fixed_discounts_lines += calculate_fixed_discount(line.product_uom_qty, line.price_unit, line.advance_discount)
            order.fixed_discounts = fixed_discounts_lines

    @api.depends_context('lang')
    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id')
    def _compute_tax_totals(self):
        super()._compute_tax_totals()
        for rec in self:
            tax_totals = rec.tax_totals
            tax_totals.update({'total_discount': formatLang(self.env, rec.fixed_discounts, currency_obj=rec.currency_id or rec.journal_id.currency_id or rec.company_id.currency_id)})
            rec.tax_totals = tax_totals
