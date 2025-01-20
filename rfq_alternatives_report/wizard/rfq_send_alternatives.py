from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseOrderAlternativeWizard(models.TransientModel):
    _name = 'purchase.order.alternative.wizard'
    _description = 'Purchase Order Alternative Wizard'

    alternative_po_ids = fields.Many2many(
        comodel_name='purchase.order',
        string='Alternative Purchase Orders',
    )
    selected_po_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Selected Purchase Order',
        required=True,
        domain="[('id', 'in', alternative_po_ids)]"
    )
    recomendation = fields.Html(
        string='Recommendation',
        help='Describe reasons to choose this alternative.'
    )

    @api.model
    def default_get(self, fields):
        res = super(PurchaseOrderAlternativeWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            purchase_order = self.env['purchase.order'].browse(active_id)
            res['alternative_po_ids'] = [(6, 0, purchase_order.alternative_po_ids.ids or [purchase_order.id])]
        return res

    def send_notification_email(self):
        if not self.selected_po_id:
            raise UserError("Please select a purchase order to proceed.")

        template = self.env.ref('rfq_alternatives_report.purchase_order_notify_alternatives')
        if not template:
            raise UserError("Email template not found.")

        # Enviar el correo basado en la plantilla
        template.with_context(
            alternative_po_ids=self.alternative_po_ids,
            selected_po_id=self.selected_po_id,
            recomendation=self.recomendation
        ).send_mail(self.selected_po_id.id, force_send=True)
