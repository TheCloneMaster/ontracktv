# Copyright (C) 2021-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('amount_total')
    def _compute_invoice_amount_text(self):
        for inv in self:
            inv.invoice_amount_text = inv.currency_id.amount_to_text(inv.amount_total).upper()

    invoice_amount_text = fields.Char(
        string='Amount in Letters',
        readonly=True,
        copy=False,
        compute="_compute_invoice_amount_text"
    )
