from odoo import models, fields, api
from functools import lru_cache

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    tax_names = fields.Char('Impuestos')

    @api.model
    def _select(self):
        return super()._select() + """,
            line.tax_names AS tax_names
        """