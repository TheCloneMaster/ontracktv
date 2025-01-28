from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)


class PartnerElectronic(models.Model):
    _inherit = "res.partner"

    # ==============================================================================================
    #                                          PARTNER
    # ==============================================================================================

    # === Partner fields === #

    expenses_provider = fields.Boolean(
        string="Proveedor de Gastos",
        default=False
    )

    invoice_template_id = fields.Many2one(
        comodel_name='ir.ui.view',
        string='Invoice Report Template',
        domain="[('type', '=', 'qweb')]",
    )

    xml_type = fields.Selection(selection=[('ice', 'ICE'), ('millicom', 'Millicom Cable')], string="Tipo de xml")

    sale_email = fields.Char('Correo de Ventas')
    purchase_email = fields.Char('Correo de Compras')