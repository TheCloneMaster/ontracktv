from odoo import models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = [_name, "tier.validation"]

    _tier_validation_state_field_is_computed = True
    _state_from = ["draft", "waiting", "confirmed", "assigned"]
    _state_to = ["done"]
    _cancel_state = ["cancel"]

    _tier_validation_manual_config = False
