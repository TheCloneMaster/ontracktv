from odoo import models, fields, api
from odoo.exceptions import UserError
import json

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_open_analytic_distribution_wizard(self):
        return {
            'name': 'Cargar Distribución Analítica',
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.analytic.distribution.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }