from odoo import models, fields, api

class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    plan_number = fields.Char(
        string="Numero de Plan",
        size=4,
        help="Número de plan de 4 dígitos"
    )
    
    secuencia_envios = fields.Many2one(
        'ir.sequence',
        string="Secuencia Envíos",
        help="Secuencia para los envíos",
        ondelete='restrict'
    )

    def _get_next_shipping_number(self):
        self.ensure_one()
        if not self.secuencia_envios:
            return False
        return self.secuencia_envios._next()

    @api.depends('payment_method_id')
    def _compute_is_bac_method(self):
        for record in self:
            record.is_bac_method = record.payment_method_id.code == 'BAC'

    is_bac_method = fields.Boolean(
        string="Es método BAC",
        compute='_compute_is_bac_method',
        store=True
    )
