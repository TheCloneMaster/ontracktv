from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountTax(models.Model):
    _inherit = "account.tax"

    tax_code = fields.Char(
        string="Tax Code"
    )
    iva_tax_desc = fields.Char(
        string="VAT Tax Rate",
        default='N/A'
    )
    iva_tax_code = fields.Char(
        string="VAT Rate Code",
        default='N/A'
    )
    has_exoneration = fields.Boolean(
        string="Has Exoneration"
    )
    percentage_exoneration = fields.Integer(
        string="Percentage of VAT Exoneration"
    )
    tax_root = fields.Many2one(
        comodel_name="account.tax",
        string="Parent Tax"
    )
    non_tax_deductible = fields.Boolean(
        string='Indicates if this tax is no deductible for Rent and VAT'
    )

    # -------------------------------------------------------------------------
    # ONCHANGE METHODS
    # -------------------------------------------------------------------------

    @api.onchange('percentage_exoneration')
    def _onchange_percentage_exoneration(self):
        self.tax_compute_exoneration()

    @api.onchange('tax_root')
    def _onchange_tax_root(self):
        self.tax_compute_exoneration()

    def tax_compute_exoneration(self):
        if self.percentage_exoneration <= 13:
            if self.tax_root:
                self.amount = self.tax_root.amount - self.percentage_exoneration
        else:
            raise UserError(_('El porcentaje no puede ser mayor a 13'))

    # def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
    #     dict_line = self._context.get('dict_line', {}) or {}
    #     if dict_line and ( (dict_line['taxes'].get(self.id) and self.tax_code == '99') or (float(dict_line['price_unit']) == 0.0) ):
    #         return dict_line['taxes'][self.id]['amount']

    #     return super(AccountTax, self)._compute_amount(
    #         base_amount=base_amount, price_unit=price_unit,
    #         quantity=quantity, product=product, partner=partner
    #     )
