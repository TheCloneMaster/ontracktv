from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    es_canje = fields.Boolean(string="Es Canje")
    no_aplica_comisiones = fields.Boolean(string="NoAplica Comisiones")
