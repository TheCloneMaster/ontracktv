# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, Command
from odoo.osv import expression
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import clean_context, formatLang
from odoo.tools import frozendict, groupby, split_every

from collections import defaultdict
from markupsafe import Markup

import ast
import math
import re



class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _prepare_tax_totals(self, base_lines, currency, tax_lines=None, is_company_currency_requested=False):
        result = super()._prepare_tax_totals(base_lines, currency, tax_lines, is_company_currency_requested)
        result['display_tax_base'] = False
        return result

    # @api.model
    # def _fix_tax_included_price(self, price, prod_taxes, line_taxes):
    #     """Subtract tax amount from price when corresponding "price included" taxes do not apply"""
    #     # FIXME get currency in param?
    #     prod_taxes = prod_taxes._origin
    #     line_taxes = line_taxes._origin
    #     incl_tax = prod_taxes.filtered(lambda tax: tax not in line_taxes and tax.price_include)
    #     if incl_tax:
    #         return incl_tax.compute_all(price)['total_excluded']
    #     return price

    # @api.model
    # def _fix_tax_included_price_company(self, price, prod_taxes, line_taxes, company_id):
    #     if company_id:
    #         #To keep the same behavior as in _compute_tax_id
    #         prod_taxes = prod_taxes.filtered(lambda tax: tax.company_id == company_id)
    #         line_taxes = line_taxes.filtered(lambda tax: tax.company_id == company_id)
    #     return self._fix_tax_included_price(price, prod_taxes, line_taxes)


# class AccountTaxRepartitionLine(models.Model):
#     _name = "account.tax.repartition.line"
#     _description = "Tax Repartition Line"
#     _order = 'document_type, repartition_type, sequence, id'
#     _check_company_auto = True
#     _check_company_domain = models.check_company_domain_parent_of

#     factor_percent = fields.Float(
#         string="%",
#         default=100,
#         required=True,
#         help="Factor to apply on the account move lines generated from this distribution line, in percents",
#     )
#     factor = fields.Float(string="Factor Ratio", compute="_compute_factor", help="Factor to apply on the account move lines generated from this distribution line")
#     repartition_type = fields.Selection(string="Based On", selection=[('base', 'Base'), ('tax', 'of tax')], required=True, default='tax', help="Base on which the factor will be applied.")
#     document_type = fields.Selection(string="Related to", selection=[('invoice', 'Invoice'), ('refund', 'Refund')], required=True)
#     account_id = fields.Many2one(string="Account",
#         comodel_name='account.account',
#         domain="[('deprecated', '=', False), ('account_type', 'not in', ('asset_receivable', 'liability_payable', 'off_balance'))]",
#         check_company=True,
#         help="Account on which to post the tax amount")
#     tag_ids = fields.Many2many(string="Tax Grids", comodel_name='account.account.tag', domain=[('applicability', '=', 'taxes')], copy=True, ondelete='restrict')
#     tax_id = fields.Many2one(comodel_name='account.tax', ondelete='cascade', check_company=True)
#     company_id = fields.Many2one(string="Company", comodel_name='res.company', related="tax_id.company_id", store=True, help="The company this distribution line belongs to.")
#     sequence = fields.Integer(string="Sequence", default=1,
#         help="The order in which distribution lines are displayed and matched. For refunds to work properly, invoice distribution lines should be arranged in the same order as the credit note distribution lines they correspond to.")
#     use_in_tax_closing = fields.Boolean(
#         string="Tax Closing Entry",
#         compute='_compute_use_in_tax_closing', store=True, readonly=False, precompute=True,
#     )

#     tag_ids_domain = fields.Binary(string="tag domain", help="Dynamic domain used for the tag that can be set on tax", compute="_compute_tag_ids_domain")

#     @api.depends('company_id.multi_vat_foreign_country_ids', 'company_id.account_fiscal_country_id')
#     def _compute_tag_ids_domain(self):
#         for rep_line in self:
#             allowed_country_ids = (False, rep_line.company_id.account_fiscal_country_id.id, *rep_line.company_id.multi_vat_foreign_country_ids.ids,)
#             rep_line.tag_ids_domain = [('applicability', '=', 'taxes'), ('country_id', 'in', allowed_country_ids)]

#     @api.depends('account_id', 'repartition_type')
#     def _compute_use_in_tax_closing(self):
#         for rep_line in self:
#             rep_line.use_in_tax_closing = (
#                 rep_line.repartition_type == 'tax'
#                 and rep_line.account_id
#                 and rep_line.account_id.internal_group not in ('income', 'expense')
#             )

#     @api.depends('factor_percent')
#     def _compute_factor(self):
#         for record in self:
#             record.factor = record.factor_percent / 100.0

#     @api.onchange('repartition_type')
#     def _onchange_repartition_type(self):
#         if self.repartition_type == 'base':
#             self.account_id = None

#     def _get_aml_target_tax_account(self, force_caba_exigibility=False):
#         """ Get the default tax account to set on a business line.

#         :return: An account.account record or an empty recordset.
#         """
#         self.ensure_one()
#         if not force_caba_exigibility and self.tax_id.tax_exigibility == 'on_payment' and not self._context.get('caba_no_transition_account'):
#             return self.tax_id.cash_basis_transition_account_id
#         else:
#             return self.account_id
