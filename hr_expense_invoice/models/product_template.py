from odoo import models, fields, api


class ProductElectronic(models.Model):
    _inherit = "product.template"

    max_amount = fields.Monetary(
        string="Monto Máximo", store=True
    )
