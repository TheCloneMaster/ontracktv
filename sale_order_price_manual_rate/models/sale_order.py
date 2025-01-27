# Copyright 2025 Mario Arias <support@cysfuturo.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    exchange_factor = fields.Float(string="Factor Tipo Cambio")

    def action_apply_exchange_factor(self):
        if self.exchange_factor:
            lines_to_recompute = self.order_line
            for line in lines_to_recompute:
                line.price_unit /= self.exchange_factor
            lines_to_recompute._compute_discount()
