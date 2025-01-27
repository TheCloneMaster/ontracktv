from odoo import _, api, fields, models, Command
from odoo.exceptions import UserError


class PurchaseRequisitionCreateAlternative(models.TransientModel):
    _inherit = 'purchase.requisition.create.alternative'

    @api.model
    def _get_alternative_line_value(self, order_line):
        res = super(PurchaseRequisitionCreateAlternative, self)._get_alternative_line_value(order_line)
        res['name'] = order_line.name
        res['analytic_distribution'] = order_line.analytic_distribution
        return res