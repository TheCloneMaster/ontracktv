from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    manual_currency = fields.Boolean(
        readonly=True,
    )
    manual_currency_rate = fields.Float(
        digits="Manual Currency",
        tracking=True,
        readonly=True,
        help="Set new currency rate to apply on the invoice\n."
        "This rate will be taken in order to convert amounts between the "
        "currency on the purchase order and last currency",
    )

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('currency_id', 'company_id', 'move_id.date', 'move_id.manual_currency_rate')
    def _compute_currency_rate(self):
        for line in self:
            if line.move_id.manual_currency:
                line.currency_rate = line.currency_id.inverse_rate and 1/line.move_id.manual_currency_rate or line.move_id.manual_currency_rate
            else:
                super(AccountMoveLine,line)._compute_currency_rate()

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id', 'move_id.manual_currency_rate')
    def _compute_totals(self):
        super()._compute_totals()
