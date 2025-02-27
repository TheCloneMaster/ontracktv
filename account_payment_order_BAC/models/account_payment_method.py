from odoo import models, api

class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['BAC'] = {
            'mode': 'multi',
            'domain': [('type', '=', 'bank')],
        }
        return res
