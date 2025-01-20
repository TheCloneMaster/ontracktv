from odoo import _, api, fields, models
from odoo.exceptions import UserError



class PurchaseRequest(models.Model):
    _inherit = "purchase.request"


    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("to_approve"):
                rec.is_editable = True
            else:
                rec.is_editable = False

    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
