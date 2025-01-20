# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('cr')
    def _get_cr_template_data(self):
        return {
            'property_account_receivable_id': 'account_account_template_0_account_receivable',
            'property_account_payable_id': 'account_account_template_0_account_payable',
            'property_account_income_categ_id': 'account_account_template_0_account_income_categ',
            'property_account_expense_categ_id': 'account_account_template_0_account_expense_categ',
        }

    @template('cr', 'res.company')
    def _get_cr_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.cr',
                'bank_account_code_prefix': '0.1112',
                'cash_account_code_prefix': '0.1111',
                'transfer_account_code_prefix': '0.1114',
                'account_default_pos_receivable_account_id': 'account_account_template_0_account_receivable',
                'income_currency_exchange_account_id': 'account_account_template_0_income_currency_exchange_account',
                'expense_currency_exchange_account_id': 'account_account_template_0_expense_currency_exchange_account',
                'account_sale_tax_id': 'account_tax_template_IV_0',
                'account_purchase_tax_id': 'account_tax_template_IV_1',
            },
        }
