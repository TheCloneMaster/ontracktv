from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    request_id = fields.Many2one('purchase.request', "Purchase Request", readonly=True)
    valid_purchase_approvers = fields.Many2many(
        'res.users',
        related='user_id.valid_purchase_approvers',
        string='Valid Purchase Approvers'
    )

    tier_validation_approver = fields.Many2one(
        'res.users',
        string="Aprobador",
        # required=True,
        domain="[('id', 'in', valid_purchase_approvers)]"
    )

    confirm_po = fields.Boolean('Permitir confirmación')
    enable_confirm_action = fields.Boolean(compute='_enable_confirm_action')

    @api.depends('confirm_po')
    def _enable_confirm_action(self):
        for p in self:
            p.enable_confirm_action = True if p.confirm_po == True else False

    def _add_tier_validation_buttons(self, node, params):
        str_element = self.env["ir.qweb"]._render(
            "tvcr_changes.tier_validation_buttons_purchase_request", params
        )
        new_node = etree.fromstring(str_element)
        return new_node

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    valid_purchase_approvers = fields.Many2many(
        'res.users',
        related='requested_by.valid_purchase_approvers',
        string='Valid Purchase Approvers'
    )

    tier_validation_approver = fields.Many2one(
        'res.users',
        string="Aprobador",
        required=True,
        domain="[('id', 'in', valid_purchase_approvers)]"
    )

    # @api.depends("state")
    # def _compute_is_editable(self):
    #     for rec in self:
    #         if rec.state in ("to_approve"):
    #             rec.is_editable = True
    #         else:
    #             rec.is_editable = False

#     is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
#        return res

class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    @api.model
    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        request_ids = self.env.context.get("active_ids", False)
        request = self.env['purchase.request'].browse(request_ids)
        result = super()._prepare_purchase_order(picking_type, group_id, company, request.name)
        result['request_id'] = request.id
        result['valid_purchase_approvers'] = [ap.id for ap in request.valid_purchase_approvers]
        result['tier_validation_approver'] = request.tier_validation_approver.id
        return result
    
class PurchaseRequisitionCreateAlternative(models.TransientModel):
    _inherit = 'purchase.requisition.create.alternative'

    def _get_alternative_values(self):
        vals = super()._get_alternative_values()
        vals['request_id'] = self.origin_po_id.request_id.id
        return vals